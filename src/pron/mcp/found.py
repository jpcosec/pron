"""What a semantic address resolves to (spec 14 §2.2): a set of documents, each with where it
came from (a tag, an enumerated field, a walk), and the lines that say why a selector the
world does not declare resolved to nothing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pron.mcp.doc_entries import DocEntries
from pron.world.doc_id import DocId


@dataclass
class Found:
    """Documents by id, each with the list of sources that put it here, and notes."""

    docs: dict[DocId, list[str]] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def add(self, doc_id: DocId, via: str) -> None:
        sources = self.docs.setdefault(doc_id, [])
        if via not in sources:
            sources.append(via)

    def intersect(self, other: "Found") -> "Found":
        """`&` (spec 02): the documents in both, with the sources of both."""
        docs = {d: v + other.docs[d] for d, v in self.docs.items() if d in other.docs}
        return Found(docs, self.notes + other.notes)

    def restrict(self, models: list[str]) -> "Found":
        docs = {d: v for d, v in self.docs.items() if d.model in models}
        return Found(docs, self.notes)

    def answer(self, entries: DocEntries) -> dict[str, Any]:
        """Every document as a row with its literal address and its sources, sorted by id."""
        rows = [
            {**entries.entry(d), "via": via}
            for d, via in sorted(self.docs.items(), key=lambda kv: str(kv[0]))
        ]
        return {"documents": rows, "notes": self.notes}
