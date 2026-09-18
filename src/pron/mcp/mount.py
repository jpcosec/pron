"""One world mounted by the MCP server (spec 14 §1): a `World` opened as it is, never linked
nor written to, and the projection that bounds what its reads may name (spec 01).
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import Any

from pron.world.doc_id import DocId, is_local
from pron.world.world import World


@dataclass
class Mount:
    """A mounted world under its name, read through one projection."""

    name: str
    world: World
    projection_name: str = "all"

    @cached_property
    def projection(self) -> dict[str, Any]:
        return self.world.projection(self.projection_name)

    def models(self) -> list[str]:
        """The models the projection names (spec 01): what a read here may resolve."""
        from pron.world.lexicon import projection_models

        return projection_models(self.world, self.projection)

    def stores(self) -> list[str | None]:
        """The projection's stores, None for the local one."""
        return [
            None if is_local(s) else s
            for s in self.projection.get("stores") or ["local"]
        ]

    def admits(self, doc_id: DocId) -> bool:
        """Whether a document is inside the projection: its model and its store."""
        return doc_id.model in self.models() and doc_id.store in self.stores()

    def require(self, doc_id: DocId) -> DocId:
        """The id itself, or LookupError when the projection does not name its model (01)."""
        if not self.admits(doc_id):
            raise LookupError(
                f"{doc_id.model} is not in projection {self.projection_name!r} of {self.name}"
            )
        return doc_id

    def require_model(self, model: str, store: str | None = None) -> None:
        """LookupError when the projection does not name the model (01)."""
        self.require(DocId.of(model, "", store))

    def summary(self) -> dict[str, Any]:
        """What `worlds_list` says of this world (spec 14 §3)."""
        return {
            "name": self.name,
            "root": str(self.world.root),
            "projection": self.projection_name,
            "models": self.models(),
        }
