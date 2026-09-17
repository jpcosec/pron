"""Reading documents by address (spec 02): the runtime documents of a model, and one
document, its payload, its hash_c and its file named the two ways callers still name it —
`(model, name, store)` and the `*_of(export_id)` forms, which take the id `store:Model:doc`.

Both forms only build a `DocId` and delegate to `DocumentsById`, where the reading is.
"""

from __future__ import annotations

from pathlib import Path

from pron.world.doc_id import LOCAL, DocId
from pron.world.storage.documents_by_id import DocumentsById


class DocumentReader(DocumentsById):
    """The documents of the local store and every linked one, read by model and name."""

    def invalidate(self) -> None:
        """Kept for callers; sldb's cache invalidates itself by the hash chain."""

    def docs_of(self, model: str, store: str | None = LOCAL) -> list:
        """Documents of a model in one store, or in every store with store='*'."""
        return [
            d
            for d in self.docs()
            if d.model_name == model
            and (store == "*" or d.store_name == (store or LOCAL))
        ]

    def doc(self, model: str, name: str, store: str | None = LOCAL):
        return self.doc_at(DocId.of(model, name, store))

    def doc_of(self, export_id: str):
        return self.doc_at(DocId.parse_plain(export_id))

    def payload(self, model: str, name: str, store: str | None = LOCAL) -> dict:
        return self.payload_at(DocId.of(model, name, store))

    def payload_of(self, export_id: str) -> dict:
        return self.payload_at(DocId.parse_plain(export_id))

    def hash_c(self, model: str, name: str, store: str | None = LOCAL) -> str:
        return self.hash_at(DocId.of(model, name, store))

    def hash_of(self, export_id: str) -> str:
        return self.hash_at(DocId.parse_plain(export_id))

    def doc_path(self, model: str, name: str, store: str | None = LOCAL) -> Path | None:
        return self.path_at(DocId.of(model, name, store))
