"""The models a store registers (spec 02, spec 12 §4): their names, indexes, Python types,
field schemas and catalog, and registering one more. A linked store's models import from
where that store lives, so every lookup here takes the store it asks.
"""

from __future__ import annotations

import builtins
from typing import Any

from pydantic import BaseModel

from sldb.api import (
    RegisteredModel,
    add_model,
    describe_model,
    describe_model_fields,
    load_registered_model,
)
from sldb.core.exceptions import SLDBModelError
from sldb.store.io import load_documents_index, load_models_index

from pron.kernel.ids import LOCAL, is_local
from pron.world.storage.linked_stores import LinkedStores
from pron.world.store_error import StoreError


class ModelRegistry(LinkedStores):
    """The registered models of the local store and of every linked one."""

    def model_names(self, store: str | None = LOCAL) -> builtins.list[str]:
        return [m.name for m in self.store_index(store).models]

    def model_entry(self, name: str, store: str | None = LOCAL):
        """The store index's entry for a model, or None when it is not registered."""
        return next((m for m in self.store_index(store).models if m.name == name), None)

    def models_index(self, name: str, store: str | None = LOCAL):
        entry = self.model_entry(name, store)
        if entry is None:
            raise StoreError(
                f"model '{name}' is not registered"
                + ("" if is_local(store) else f" in store '{store}'")
            )
        return load_models_index(self.root_of(store) / entry.models_index)

    def model_type(self, name: str, store: str | None = LOCAL) -> type[BaseModel]:
        try:
            return load_registered_model(
                self.sp_of(store), name, self.pythonpath
            ).model_type
        except Exception:  # noqa: BLE001 - a linked store's models import from where that store lives
            if is_local(store):
                raise
            return load_registered_model(
                self.sp_of(store), name, str(self.root_of(store))
            ).model_type

    def registration(self, model: str, store: str | None = LOCAL) -> RegisteredModel:
        """sldb's model type, store entry and store index for tracking a document of `model`."""
        return load_registered_model(
            self.sp_of(store), model, self.pythonpath_for(store, model)
        )

    def pythonpath_for(self, store: str | None, model: str) -> str:
        """Where `model` imports from: this world's pythonpath, or a linked store's own root."""
        if is_local(store):
            return self.pythonpath
        try:
            load_registered_model(self.sp_of(store), model, self.pythonpath)
            return self.pythonpath
        except Exception:  # noqa: BLE001
            return str(self.root_of(store))

    def schema(
        self, name: str, store: str | None = LOCAL
    ) -> builtins.list[dict[str, Any]]:
        """Fields of a model: name, kind, required, enum, annotation, description."""
        return [  # `enum` only when the field has one, as sldb serve's schema endpoint
            f.model_dump(exclude_none=True)
            for f in describe_model_fields(self.model_type(name, store))
        ]

    def register_model(self, ref: str) -> bool:
        try:
            add_model(self.sp, ref, self.pythonpath)
        except SLDBModelError:
            return False
        return True

    def model_catalog(self, store: str | None = LOCAL) -> builtins.list[dict[str, Any]]:
        """Registered models with version, canonical, family and document count."""
        root = self.root_of(store)
        out = []
        for entry in sorted(self.store_index(store).models, key=lambda m: m.name):
            m_idx = self.models_index(entry.name, store)
            d_idx = load_documents_index(root / m_idx.documents_index)
            out.append(
                {
                    "name": entry.name,
                    "model_ref": entry.model_ref,
                    "path": entry.path,
                    "version": m_idx.version,
                    "canonical": m_idx.canonical,
                    "family": m_idx.family,
                    "semantics": list(m_idx.semantics),
                    "documents": len(d_idx.documents),
                }
            )
        return out

    def model_detail(self, name: str, store: str | None = LOCAL) -> dict[str, Any]:
        """The model as sldb's `models show` builds it: `{"model": {...fields, version...}}`."""
        description = describe_model(self.sp_of(store), name, self.pythonpath)
        return {"model": description.model_dump()}
