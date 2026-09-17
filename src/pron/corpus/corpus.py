"""The indexed corpus of a world (spec 12 §5b): which documents a consumer can retrieve
by similarity, kept fresh against the store.

A runtime that retrieves documents by meaning needs the same six things every time: pick
the documents, get the text that represents each one, know the content hash so a reindex
embeds only what changed, persist the vectors outside git, rank a query, and audit that
the index matches the store. All of that is general and lives here. What is not general
is which models enter and what text represents a document: that is the consumer's policy,
declared once as an `IndexProjection` and passed in.

Identity is always the export id (`Model:doc`, `store:Model:doc`), never the bare name:
two stores of a federated world may hold the same document name.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Sequence

from pron.corpus.corpus_entry import CorpusEntry
from pron.corpus.hit import Hit
from pron.corpus.index_projection import IndexProjection
from pron.kernel.ids import join_id
from pron.world.matching.document_index import DocumentIndex
from pron.world.matching.matcher import Matcher

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.world.world import World


class Corpus:
    """The documents of a world that can be retrieved by similarity, and their index.

    The index file lives in `.pron/`, outside git, named by embedder and text projection,
    so two projections of the same world never overwrite each other's vectors.
    """

    def __init__(
        self,
        world: "World",
        projection: IndexProjection | None = None,
        embedder: Any | None = None,
        matcher: Matcher | None = None,
    ) -> None:
        self.world = world
        self.projection = projection or IndexProjection()
        self.matcher = matcher or Matcher(embedder)
        self._index: DocumentIndex | None = None

    # -- the index ------------------------------------------------------------

    @property
    def index_path(self) -> Path:
        safe = self.matcher.id().replace("/", "_").replace(":", "_")
        text_id = self.projection.text_id
        name = f"docs.{safe}.json" if text_id == "summary" else f"docs.{text_id}.{safe}.json"
        return self.world.derived_dir / name

    @property
    def index(self) -> DocumentIndex:
        if self._index is None:
            self._index = DocumentIndex(self.matcher, self.index_path)
        return self._index

    # -- the corpus -----------------------------------------------------------

    def entries(self) -> list[CorpusEntry]:
        """Every document the projection admits, with its text, hash and export id."""
        out: list[CorpusEntry] = []
        for record in self.world.store.docs():
            model = record.model_name or ""
            if not self.projection.admits(model):
                continue
            store = record.store_name
            if self.projection.stores is not None and store not in self.projection.stores:
                continue
            payload = record.payload or {}
            text = self.projection.text(payload)
            if not text:
                continue
            out.append(
                CorpusEntry(
                    id=join_id(store, model, record.name),
                    model=model,
                    name=record.name,
                    store=store,
                    text=text,
                    hash=self.world.store.hash_c(model, record.name, store),
                    payload=payload,
                    tags=tuple(record.semantic_tags or ()),
                )
            )
        return out

    def refresh(self) -> dict[str, int]:
        """Embed what changed, keep what did not, drop what left the corpus."""
        return self.index.index((e.id, e.hash, e.text) for e in self.entries())

    def refresh_if_stale(self) -> dict[str, int] | None:
        """Refresh only when the index does not match the store. Returns the report, or None."""
        report = self.audit()
        if report["missing"] or report["stale"] or report["orphan"]:
            return self.refresh()
        return None

    def audit(self) -> dict[str, Any]:
        """What the index has against what the corpus holds: documents never indexed
        (`missing`), indexed from other content (`stale`), indexed and no longer in the
        corpus (`orphan`)."""
        entries = {e.id: e for e in self.entries()}
        indexed = self.index.entries_by_hash()
        missing = sorted(k for k in entries if k not in indexed)
        stale = sorted(k for k, e in entries.items() if k in indexed and indexed[k] != e.hash)
        orphan = sorted(k for k in indexed if k not in entries)
        return {
            "embedder": self.matcher.id(),
            "text": self.projection.text_id,
            "corpus": len(entries),
            "indexed": len(indexed),
            "missing": missing,
            "stale": stale,
            "orphan": orphan,
            "clean": not (missing or stale or orphan),
        }

    # -- retrieval ------------------------------------------------------------

    def rank(
        self,
        query: str,
        k: int | None = None,
        threshold: float = 0.0,
        among: Sequence[str] | None = None,
        refresh: bool = True,
    ) -> list[Hit]:
        """Documents ranked by similarity, best first. `among` restricts to those export
        ids. With refresh, the index is brought up to date first (the default: a consumer
        that never reindexes ranks against a stale world)."""
        if refresh:
            self.refresh_if_stale()
        by_id = {e.id: e for e in self.entries()}
        allowed = set(among) if among is not None else None
        hits: list[Hit] = []
        for doc_id, score in self.index.rank(query, k=None, threshold=threshold):
            if allowed is not None and doc_id not in allowed:
                continue
            entry = by_id.get(doc_id)
            if entry is None:
                continue
            hits.append(
                Hit(
                    id=entry.id,
                    model=entry.model,
                    name=entry.name,
                    score=round(score, 4),
                    payload=entry.payload,
                    tags=entry.tags,
                )
            )
            if k is not None and len(hits) >= k:
                break
        return hits

    def vectors(self) -> dict[str, list[float]]:
        """export id -> vector, for a consumer that projects or compares them itself."""
        return self.index.vectors()
