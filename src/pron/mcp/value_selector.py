"""`@{valor}` (spec 14 §2.2): the documents the world declares with that value, as a tag
(their `tagged_as` edge, spec 10 §2.3, or their `tags` field) and as a value of a field whose
type enumerates it (`Literal`, `Enum`; spec 05). The server knows no value of its own.
"""

from __future__ import annotations

from typing import Any

from pron.mcp.found import Found
from pron.mcp.mount import Mount
from pron.world.doc_id import DocId
from pron.world.graph import bare, kind, tag_id


def holds(value: Any, wanted: str) -> bool:
    """A field holds the value itself, or a list with it."""
    items = value if isinstance(value, list) else [value]
    return wanted in [str(v) for v in items]


class ValueSelector:
    """One declared value to the documents that carry it, each saying from where."""

    def __init__(self, mount: Mount) -> None:
        self.mount = mount
        self.world = mount.world

    def __call__(self, value: str) -> Found:
        found = Found()
        self._tagged(value, found)
        self._enumerated(value, found)
        if not found.docs:
            found.notes.append(
                f"@{value}: neither a tag nor an enumerated value this world declares"
            )
        return found

    def _tagged(self, value: str, found: Found) -> None:
        for node in self.world.graph.sources(tag_id(value), "tagged_as"):
            if kind(node) == "document":
                self._keep(DocId.parse(bare(node)), "tag", found)
        for record in self.world.store.docs():
            if holds((record.payload or {}).get("tags"), value):
                doc_id = DocId.of(record.model_name, record.name, record.store_name)
                self._keep(doc_id, "tag", found)

    def _enumerated(self, value: str, found: Found) -> None:
        for model in self.mount.models():
            for spec in self.world.schema(model):
                if value in [str(v) for v in spec.get("enum") or []]:
                    self._field(model, spec["name"], value, found)

    def _field(self, model: str, name: str, value: str, found: Found) -> None:
        for store in self.mount.stores():
            for record in self.world.store.docs_of(model, store):
                if holds((record.payload or {}).get(name), value):
                    doc_id = DocId.of(model, record.name, store)
                    self._keep(doc_id, f"enum:{model}.{name}", found)

    def _keep(self, doc_id: DocId, via: str, found: Found) -> None:
        if self.mount.admits(doc_id):
            found.add(doc_id, via)
