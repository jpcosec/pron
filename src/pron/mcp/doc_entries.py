"""How a document shows in an answer of the MCP surface (spec 14 §2): always with its literal
address, so an agent can step down from a set to one document and keep walking.
"""

from __future__ import annotations

from typing import Any

from pron.mcp.mount import Mount
from pron.mcp.kb_uri import literal_uri
from pron.world.doc_id import DocId


def title_of(doc_id: DocId, payload: dict[str, Any]) -> str:
    """The document's own title, else its name field, else its document name."""
    return str(payload.get("title") or payload.get("name") or doc_id.name)


class DocEntries:
    """Documents of one mounted world as answer rows: address, id, model, title."""

    def __init__(self, mount: Mount) -> None:
        self.mount = mount

    def uri(self, doc_id: DocId, *rest: str | int) -> str:
        return literal_uri(self.mount.name, doc_id, *rest)

    def entry(
        self, doc_id: DocId, payload: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """One row; the payload is read when not given."""
        if payload is None:
            payload = self.mount.world.store.payload(doc_id)
        return {
            "uri": self.uri(doc_id),
            "id": str(doc_id),
            "model": doc_id.model,
            "title": title_of(doc_id, payload),
        }

    def of_record(self, record: Any) -> dict[str, Any]:
        """A row for one of sldb's runtime documents."""
        doc_id = DocId.of(record.model_name, record.name, record.store_name)
        return self.entry(doc_id, record.payload or {})

    def records(self) -> list[Any]:
        """The runtime documents inside the projection, in the store's order."""
        admits = self.mount.admits
        return [
            r
            for r in self.mount.world.store.docs()
            if admits(DocId.of(r.model_name or "", r.name, r.store_name))
        ]
