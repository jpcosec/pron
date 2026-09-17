"""Reading documents by address (spec 02): the runtime documents of every store from sldb's
cache, one document or a model's documents, a payload as a JSON-safe copy, and what the
store's index says of a document (its hash_c, its file).

sldb caches the runtime documents by the store's hash chain, so reading them here costs
nothing and is never stale. The `*_of(export_id)` forms take the id `store:Model:doc`.
"""

from __future__ import annotations

import json
from pathlib import Path

from sldb.cli.model_utils import resolve_model_ref
from sldb.store.io import load_documents_index
from sldb.store.query import load_runtime_documents

from pron.kernel.ids import LOCAL, is_local, split_id
from pron.world.storage.model_registry import ModelRegistry
from pron.world.store_error import StoreError


class DocumentReader(ModelRegistry):
    """The documents of the local store and every linked one, read by model and name."""

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

    def doc(self, model: str, name: str, store: str | None = LOCAL):
        for d in self.docs():
            if (
                d.model_name == model
                and d.name == name
                and d.store_name == (store or LOCAL)
            ):
                return d
        return None

    def doc_of(self, export_id: str):
        store, model, name = split_id(export_id)
        return self.doc(model, name, store)

    def payload(self, model: str, name: str, store: str | None = LOCAL) -> dict:
        d = self.doc(model, name, store)
        if d is None:
            raise StoreError(
                f"no {model} named '{name}'"
                + ("" if is_local(store) else f" in store '{store}'")
            )
        return json.loads(json.dumps(d.payload))

    def payload_of(self, export_id: str) -> dict:
        store, model, name = split_id(export_id)
        return self.payload(model, name, store)

    def hash_c(self, model: str, name: str, store: str | None = LOCAL) -> str:
        found = self._indexed(model, name, store)
        return found[1].hash_c if found else ""

    def hash_of(self, export_id: str) -> str:
        store, model, name = split_id(export_id)
        return self.hash_c(model, name, store)

    def doc_path(self, model: str, name: str, store: str | None = LOCAL) -> Path | None:
        found = self._indexed(model, name, store)
        return found[0] / found[1].path if found else None

    def _indexed(self, model: str, name: str, store: str | None) -> tuple | None:
        """(store root, documents-index entry) of one document, or None when it is not tracked."""
        m_idx = self.models_index(model, store)
        root = self.root_of(store)
        for d in load_documents_index(root / m_idx.documents_index).documents:
            if d.name == name:
                return root, d
        return None
