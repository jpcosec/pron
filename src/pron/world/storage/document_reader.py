"""Reading documents by address (spec 02): the runtime documents of every store from sldb's
cache, a model's documents, and one document named by its `DocId` — the document itself,
its payload as a JSON-safe copy, and what the store's index says of it (its hash_c, its file).

sldb caches the runtime documents by the store's hash chain, so reading them here costs
nothing and is never stale.
"""

from __future__ import annotations

import json
from pathlib import Path

from sldb.api import resolve_model_ref

# Excepción deliberada: sldb.api no expone lectura de índices ni del caché de documentos runtime; solo lookup por nombre.
from sldb.store.io import load_documents_index
from sldb.store.query import load_runtime_documents

from pron.world.doc_id import LOCAL, DocId
from pron.world.storage.model_registry import ModelRegistry
from pron.world.store_error import StoreError


def in_store(doc_id: DocId) -> str:
    """The ' in store …' an error about a linked store's document ends with."""
    return "" if doc_id.is_local else f" in store '{doc_id.store}'"


class DocumentReader(ModelRegistry):
    """The documents of the local store and every linked one; one document by its `DocId`."""

    def docs(self) -> list:
        """The runtime documents of the local store and every linked one, from sldb's cache."""
        return load_runtime_documents(
            self.sp,
            resolve_model_ref,
            self.pythonpath,
            include_linked=bool(self.store_index().stores),
        )

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

    def doc(self, doc_id: DocId):
        store = doc_id.store or LOCAL
        for d in self.docs():
            if (
                d.model_name == doc_id.model
                and d.name == doc_id.name
                and d.store_name == store
            ):
                return d
        return None

    def payload(self, doc_id: DocId) -> dict:
        d = self.doc(doc_id)
        if d is None:
            raise StoreError(
                f"no {doc_id.model} named '{doc_id.name}'" + in_store(doc_id)
            )
        return json.loads(json.dumps(d.payload))

    def hash_c(self, doc_id: DocId) -> str:
        found = self._indexed(doc_id)
        return found[1].hash_c if found else ""

    def doc_path(self, doc_id: DocId) -> Path | None:
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
