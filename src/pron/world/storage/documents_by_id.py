"""Reading one document by its `DocId` (spec 02): the document itself, its payload as a
JSON-safe copy, and what the store's index says of it (its hash_c, its file).

This is the one form every read of a document goes through; the `(model, name, store)` and
`*_of(export_id)` forms of `DocumentReader` build a `DocId` and come here. sldb caches the
runtime documents by the store's hash chain, so reading them costs nothing and is never stale.
"""

from __future__ import annotations

import json
from pathlib import Path

from sldb.api import resolve_model_ref
from sldb.store.io import load_documents_index
from sldb.store.query import load_runtime_documents

from pron.world.doc_id import LOCAL, DocId
from pron.world.storage.model_registry import ModelRegistry
from pron.world.store_error import StoreError


def in_store(doc_id: DocId) -> str:
    """The ' in store …' an error about a linked store's document ends with."""
    return "" if doc_id.is_local else f" in store '{doc_id.store}'"


class DocumentsById(ModelRegistry):
    """The documents of the local store and every linked one, each read by its `DocId`."""

    def docs(self) -> list:
        """The runtime documents of the local store and every linked one, from sldb's cache."""
        return load_runtime_documents(
            self.sp,
            resolve_model_ref,
            self.pythonpath,
            include_linked=bool(self.store_index().stores),
        )

    def doc_at(self, doc_id: DocId):
        store = doc_id.store or LOCAL
        for d in self.docs():
            if (
                d.model_name == doc_id.model
                and d.name == doc_id.name
                and d.store_name == store
            ):
                return d
        return None

    def payload_at(self, doc_id: DocId) -> dict:
        d = self.doc_at(doc_id)
        if d is None:
            raise StoreError(
                f"no {doc_id.model} named '{doc_id.name}'" + in_store(doc_id)
            )
        return json.loads(json.dumps(d.payload))

    def hash_at(self, doc_id: DocId) -> str:
        found = self._indexed(doc_id)
        return found[1].hash_c if found else ""

    def path_at(self, doc_id: DocId) -> Path | None:
        found = self._indexed(doc_id)
        return found[0] / found[1].path if found else None

    def _indexed(self, doc_id: DocId) -> tuple | None:
        """(store root, documents-index entry) of one document, or None when it is not tracked."""
        m_idx = self.models_index(doc_id.model, doc_id.store)
        root = self.root_of(doc_id.store)
        for d in load_documents_index(root / m_idx.documents_index).documents:
            if d.name == doc_id.name:
                return root, d
        return None
