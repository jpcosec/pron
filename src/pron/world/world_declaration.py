"""A world's declaration (spec 01): the stores it spans, the models they register with their
fields, types, bases and hashes, and the relation types they declare. Read from the store,
never written here.
"""

from __future__ import annotations

from typing import Any

from pron.kernel.ids import LOCAL, is_local
from pron.world.store import Store
from pron.world.store_error import StoreError


class WorldDeclaration:
    """What one store and the stores it links declare."""

    def __init__(self, store: Store) -> None:
        self.store = store

    def stores(self) -> list[str]:
        """'local' and the names of the stores linked into this one (spec 01)."""
        return self.store.names()

    def model_names(self, store: str | None = LOCAL) -> list[str]:
        return self.store.model_names(store)

    def model_store(self, name: str, stores: list[str] | None = None) -> str | None:
        """The first of `stores` (default: local, then linked) that registers the model, or None."""
        for s in stores or self.stores():
            if name in self.model_names(s):
                return None if is_local(s) else s
        return None

    def schema(
        self, name: str, stores: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """The model's fields, from whichever store registers it."""
        return self.store.schema(name, self.model_store(name, stores))

    def model_type(self, name: str, stores: list[str] | None = None) -> type:
        return self.store.model_type(name, self.model_store(name, stores))

    def model_hashes(self) -> dict[str, str]:
        return {
            m.name: self.store.models_index(m.name).hash_b
            for m in self.store.store_index().models
        }

    def base_models(self, name: str) -> list[str]:
        for s in self.stores():
            try:
                return list(self.store.models_index(name, s).base_models)
            except StoreError:
                continue
        return []

    def family_of(self, name: str) -> list[str]:
        """The model and its bases, nearest first."""
        return [name, *self.base_models(name)]

    def relation_types(
        self, stores: list[str] | None = None
    ) -> dict[str, dict[str, Any]]:
        """name -> RelationTypeDoc payload, read from the given stores (default: every store);
        the first store that declares a name wins."""
        out: dict[str, dict[str, Any]] = {}
        for s in stores or self.stores():
            if "RelationTypeDoc" not in self.model_names(s):
                continue
            for d in self.store.docs_of("RelationTypeDoc", s):
                out.setdefault(
                    d.payload["name"],
                    dict(d.payload, doc=d.name, store=None if is_local(s) else s),
                )
        return out
