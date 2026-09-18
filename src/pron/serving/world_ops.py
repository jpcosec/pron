"""The ops that read or refresh the daemon's world itself (spec 11 §8, 12 §3): ping, a
payload by address (inside the named projection, if any), one graph or world method by
name from an allowed list, and a refresh.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

from pron.kernel.ids import is_local
from pron.world.doc_id import DocId

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.serve import Server

GRAPH_METHODS = (
    "has_node",
    "node",
    "node_type",
    "edges_from",
    "edges_to",
    "exists",
    "nodes_of_type",
    "targets",
    "sources",
    "roots",
    "children",
    "parent",
    "descendants",
    "neighbors_via",
    "built_from",
    "available",
)
WORLD_METHODS = (
    "model_names",
    "family_of",
    "relation_types",
    "projection",
    "hash_mundo",
    "model_hashes",
    "graph_is_fresh",
)


class WorldOps:
    """The world ops of one server, each `(name, req, foreign) -> answer`."""

    def __init__(self, server: "Server") -> None:
        self.server = server

    def ping(self, name: str, req: dict[str, Any], foreign: bool) -> dict[str, Any]:
        world = self.server.world
        return {
            "ok": True,
            "world": str(world.root),
            "name": name if not is_local(name) else self.server.names.own(),
            "hash": world.hash_mundo(),
            "sessions": len(self.server.pool.sessions),
            "pid": os.getpid(),
        }

    def payload(self, name: str, req: dict[str, Any], foreign: bool) -> dict[str, Any]:
        self._in_projection(name, req, req["model"])
        world = self.server.world
        world.store.begin_operation()
        return {
            "ok": True,
            "payload": world.store.payload(DocId.of(req["model"], req["doc"], name)),
        }

    def _in_projection(self, name: str, req: dict[str, Any], model: str) -> None:
        """A payload read names a projection or none; with one, the model must be in it (01)."""
        pname = req.get("projection")
        if not pname:
            return
        from pron.world.lexicon import projection_models

        world = self.server.world
        if model not in projection_models(
            world, world.projection(pname, None if is_local(name) else name)
        ):
            raise PermissionError(f"{model} is not in projection {pname!r}")

    def graph(self, name: str, req: dict[str, Any], foreign: bool) -> dict[str, Any]:
        return {
            "ok": True,
            "result": _call(self.server.world.graph, GRAPH_METHODS, req),
        }

    def world(self, name: str, req: dict[str, Any], foreign: bool) -> dict[str, Any]:
        return {"ok": True, "result": _call(self.server.world, WORLD_METHODS, req)}

    def refresh(self, name: str, req: dict[str, Any], foreign: bool) -> dict[str, Any]:
        return {"ok": True, "report": self.server.world.refresh()}


def _call(target: Any, allowed: tuple[str, ...], req: dict[str, Any]) -> Any:
    """One method of the world or the graph, by name, from the allowed list, with json args."""
    method = req.get("method", "")
    if method not in allowed:
        raise ValueError(f"unknown method {method!r}; one of {', '.join(allowed)}")
    args = req.get("args") or {}
    if "exclude_prefixes" in args:
        args["exclude_prefixes"] = tuple(args["exclude_prefixes"])
    return getattr(target, method)(**args)
