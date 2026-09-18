"""Ranked search (spec 14 §3.3): documents ordered by similarity with the corpus index
(`pron.corpus`), the only free-text input of the MCP surface. It returns addresses with
their score and says which method ranked them; it interprets nothing and never writes in
the world (its index lives in `.pron/`, derived and outside git).
"""

from __future__ import annotations

from typing import Any, Sequence

from pron.corpus import Corpus, IndexProjection, summary_text
from pron.mcp.doc_entries import DocEntries
from pron.mcp.mount import Mount
from pron.world.doc_id import DocId


def document_text(payload: dict[str, Any]) -> str:
    """A document's summary; without one, its scalar fields as `field value` words."""
    return summary_text(payload) or " ".join(
        f"{k} {v}"
        for k, v in payload.items()
        if isinstance(v, (str, int, float)) and v != ""
    )


class RankedSearch:
    """Text to the projection's documents, best first."""

    def __init__(self, mount: Mount) -> None:
        self.mount = mount
        self.corpus = Corpus(
            mount.world,
            IndexProjection.of(
                models=mount.models(), text=document_text, text_id="mcp"
            ),
        )

    def __call__(self, text: str, among: Sequence[str] | None = None) -> dict[str, Any]:
        """Every scored document, best first: the caller pages them (spec 14 §3.3)."""
        entries = DocEntries(self.mount)
        rows = []
        for hit in self.corpus.rank(text, among=among):
            doc_id = DocId.parse(hit.id)
            if self.mount.admits(doc_id):
                rows.append({**entries.entry(doc_id, hit.payload), "score": hit.score})
        return {"query": text, "method": self.corpus.matcher.id(), "documents": rows}
