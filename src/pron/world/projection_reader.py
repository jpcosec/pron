"""Reading a projection (spec 01, spec 12 §6): a ProjectionDoc payload by name, or 'all'
synthesized when no document declares it, read from the local store or from a linked one
whose 'local' then means that store.
"""

from __future__ import annotations

from typing import Any

from pron.kernel.ids import is_local
from pron.world.doc_id import DocId
from pron.world.store import Store
from pron.world.store_error import StoreError


class ProjectionReader:
    """The projections of one store and the stores it links."""

    def __init__(self, store: Store) -> None:
        self.store = store

    def __call__(self, name: str = "all", home: str | None = None) -> dict[str, Any]:
        """A ProjectionDoc payload; 'all' is synthesized when no document declares it. With
        `home`, the projection is read from that linked store and its 'local' means that
        store: a node's own projections work the same alone and through a daemon (12 §6)."""
        d = (
            self.store.doc(DocId.of("ProjectionDoc", f"projection-{name}", home))
            if "ProjectionDoc" in self.store.model_names(home)
            else None
        )
        if d is not None:
            return self._rebind(dict(d.payload), home)
        if name != "all":
            raise StoreError(
                f"no projection named '{name}'"
                + (f" in store '{home}'" if not is_local(home) else "")
            )
        return self._rebind(self._all(), home)

    @staticmethod
    def _all() -> dict[str, Any]:
        from pron.models.projection import ACTIONS

        return {
            "name": "all",
            "stores": ["local"],
            "models": [],
            "relations": [],
            "actions": list(ACTIONS),
            "aliases": ["all"],
            "naming": {},
            "display": {},
            "key": {},
            "matching": {"neighbors": 3, "threshold": 0.55},
            "exposed": False,
            "description": "",
        }

    @staticmethod
    def _rebind(projection: dict[str, Any], home: str | None) -> dict[str, Any]:
        """A projection read from a linked store: its 'local' is that store."""
        if is_local(home):
            return projection
        projection["stores"] = [
            home if is_local(s) else s for s in (projection.get("stores") or ["local"])
        ]
        projection["home"] = home
        return projection
