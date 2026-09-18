"""The literal plane (spec 14 §2.1): a model, a document, a field, an item of a list field,
each a single destination. A document of a linked store is named with its store prefix
(`A:Model`, spec 10 §2.2); a model outside the projection does not resolve (spec 01).
"""

from __future__ import annotations

from typing import Any

from pron.mcp.doc_entries import DocEntries
from pron.mcp.mount import Mount
from pron.world.doc_id import DocId


def model_ref(segment: str) -> tuple[str | None, str]:
    """`Model` or `A:Model` as (store, model)."""
    store, _, model = segment.rpartition(":")
    return store or None, model


class LiteralReads:
    """Reads by literal address over one mounted world."""

    def __init__(self, mount: Mount) -> None:
        self.mount = mount
        self.entries = DocEntries(mount)

    def __call__(self, segments: list[str]) -> dict[str, Any]:
        store, model = model_ref(segments[0])
        if len(segments) == 1:
            return self.model(store, model)
        doc_id = self.mount.require(DocId.of(model, segments[1], store))
        if len(segments) == 2:
            return self.document(doc_id)
        if len(segments) > 4:
            raise LookupError(
                f"a literal address ends at an item: /{'/'.join(segments)}"
            )
        return self.field(doc_id, segments[2], segments[3:])

    def model(self, store: str | None, model: str) -> dict[str, Any]:
        """The documents of a model: address, id, title."""
        self.mount.require_model(model, store)
        docs = [
            self.entries.of_record(r)
            for r in self.mount.world.store.docs_of(model, store)
        ]
        return {"model": model, "store": store, "documents": docs}

    def document(self, doc_id: DocId) -> dict[str, Any]:
        """The whole payload (spec 12 §4), with the document's row."""
        payload = self.mount.world.payload(doc_id.model, doc_id.name, doc_id.store)
        return {**self.entries.entry(doc_id, payload), "payload": payload}

    def field(self, doc_id: DocId, name: str, item: list[str]) -> dict[str, Any]:
        """One field's value, or item `i` of a list field."""
        payload = self.mount.world.payload(doc_id.model, doc_id.name, doc_id.store)
        if name not in payload:
            raise LookupError(f"{doc_id} has no field {name!r}")
        value = payload[name]
        if item:
            value = self._item(value, item[0], f"{doc_id}/{name}")
        uri = self.entries.uri(doc_id, name, *item)
        return {"uri": uri, "id": str(doc_id), "field": name, "value": value}

    @staticmethod
    def _item(value: Any, index: str, where: str) -> Any:
        if not isinstance(value, list):
            raise LookupError(f"{where} is not a list")
        try:
            return value[int(index)]
        except (ValueError, IndexError):
            raise LookupError(f"{where} has no item {index!r}") from None
