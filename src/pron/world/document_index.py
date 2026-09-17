"""Documents of a world ranked by similarity to a query (spec 05 §Calce aproximado, 11 §2).
The vectors live in one derived file outside git, keyed by the document's content hash, so a
re-index embeds only what changed. pron never decides what to do with a rank; it offers it.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from pron.world.matcher import Matcher, cosine


class DocumentIndex:
    """Documents of a world ranked by similarity to a query (spec 05 §Calce aproximado, 11 §2):
    the vectors live in one derived file outside git, keyed by the document's content hash,
    so a re-index embeds only what changed. With a Matcher that has no Embedder there are no
    vectors: the texts are kept and ranked with difflib, and the file says which it is.
    pron never decides what to do with a rank; it offers it."""

    def __init__(self, matcher: Matcher, cache_path: Path):
        self.matcher = matcher
        self.cache_path = Path(cache_path)
        self._entries: dict[str, dict] = {}
        self._load()

    @property
    def embedder_id(self) -> str:
        return self.matcher.id()

    def _load(self) -> None:
        self._entries = {}
        if not self.cache_path.exists():
            return
        try:
            data = json.loads(self.cache_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        if data.get("embedder") == self.embedder_id:
            self._entries = data.get("entries", {}) or {}

    def _save(self) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_text(
            json.dumps({"embedder": self.embedder_id, "entries": self._entries}),
            encoding="utf-8",
        )

    def index(self, items: Iterable[tuple[str, str, str]]) -> dict[str, int]:
        """items are (key, content_hash, text). Embeds the keys whose hash is new or changed,
        keeps the rest, drops the keys that did not come. Returns {embedded, reused, dropped}."""
        items = list(items)
        keep: dict[str, dict] = {}
        todo: list[tuple[str, str, str]] = []
        reused = 0
        for key, h, text in items:
            prev = self._entries.get(key)
            if prev is not None and prev.get("hash") == h:
                keep[key] = prev
                reused += 1
            else:
                todo.append((key, h, text))
        if self.matcher.embedder is None:
            for key, h, text in todo:
                keep[key] = {"hash": h, "text": text}
        elif todo:
            vectors = self.matcher.embedder.embed([t for _, _, t in todo])
            for (key, h, _), v in zip(todo, vectors):
                keep[key] = {"hash": h, "vector": [float(x) for x in v]}
        dropped = len(set(self._entries) - set(keep))
        self._entries = keep
        self._save()
        return {"embedded": len(todo), "reused": reused, "dropped": dropped}

    def keys(self) -> list[str]:
        return sorted(self._entries)

    def entries_by_hash(self) -> dict[str, str]:
        """key -> the content hash it was indexed from, for a consumer that audits the
        index against the store it came from."""
        return {k: e.get("hash", "") for k, e in self._entries.items()}

    def vectors(self) -> dict[str, list[float]]:
        """key -> vector for every indexed document that has one (none without an Embedder).
        For consumers that project or compare the vectors themselves, e.g. a 2D map of a world."""
        return {k: list(e["vector"]) for k, e in self._entries.items() if "vector" in e}

    def rank(
        self, query: str, k: int | None = None, threshold: float = 0.0
    ) -> list[tuple[str, float]]:
        """[(key, score)] best first, above threshold; cosine over the vectors, or difflib
        over the kept texts when there is no Embedder."""
        if not self._entries:
            return []
        if self.matcher.embedder is None:
            scored = [
                (key, self.matcher.fallback.similarity(query, e.get("text", "")))
                for key, e in self._entries.items()
            ]
        else:
            q = self.matcher.embedder.embed([query])[0]
            scored = [
                (key, cosine(q, e["vector"]))
                for key, e in self._entries.items()
                if "vector" in e
            ]
        out = sorted(
            ((key, s) for key, s in scored if s >= threshold),
            key=lambda kv: (-kv[1], kv[0]),
        )
        return out[:k] if k is not None else out
