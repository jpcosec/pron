"""The only door to kgdb: read edges of the typed graph the projector built (spec 03, 10).

pron never writes to kgdb. The graph lives at <world>/.pron/graph.nx.json, built by
`kgdb ingest --store` through its library (see pron.world.World.refresh). It is fresh
when the model hashes it was built from are the store's current ones (the ledger's
model excluded); otherwise every read says so and callers fall back to sldb.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

GRAPH_RELPATH = Path(".pron") / "graph.nx.json"
LEDGER_MODEL = "MoveDoc"


def doc_id(export_id: str) -> str:
    return f"sldb://document/{export_id}"


def model_id(name: str) -> str:
    return f"sldb://model/{name}"


def relation_type_id(name: str) -> str:
    return f"sldb://relation_type/{name}"


def field_id(model: str, field: str) -> str:
    return f"sldb://field/{model}.{field}"


class Graph:
    """Reads the node-link JSON kgdb saved, without networkx: nodes by id, edges indexed by
    source and by target. Reading a file format is not assembling a graph."""

    def __init__(self, root: str | Path) -> None:
        self.path = Path(root).resolve() / GRAPH_RELPATH
        self._nodes: dict[str, dict[str, Any]] | None = None
        self._out: dict[str, list[dict[str, Any]]] = {}
        self._in: dict[str, list[dict[str, Any]]] = {}

    def available(self) -> bool:
        return self.path.exists()

    def load(self) -> dict[str, dict[str, Any]]:
        if self._nodes is None:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            self._nodes = {n["id"]: n for n in data.get("nodes", [])}
            self._out, self._in = {}, {}
            for link in data.get("links", data.get("edges", [])):
                e = {"source": link["source"], "target": link["target"], "relation": link.get("relation", link.get("key")), "metadata": link.get("metadata", {}) or {}}
                self._out.setdefault(e["source"], []).append(e)
                self._in.setdefault(e["target"], []).append(e)
        return self._nodes

    def reload(self) -> None:
        self._nodes = None

    def metadata(self) -> dict[str, Any]:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return data.get("graph", {}) or {}

    def built_from(self) -> dict[str, str]:
        """Model name -> hash_b the snapshot was built from (ledger excluded)."""
        models = self.metadata().get("models", {}) or {}
        return {k: v for k, v in models.items() if k != LEDGER_MODEL}

    def is_fresh(self, current_models: dict[str, str]) -> bool:
        if not self.available():
            return False
        current = {k: v for k, v in current_models.items() if k != LEDGER_MODEL}
        return self.built_from() == current

    def has_node(self, node_id: str) -> bool:
        return node_id in self.load()

    def node(self, node_id: str) -> dict[str, Any]:
        return self.load().get(node_id, {}).get("schema", {}) or {}

    def edges_from(self, node_id: str, relation: str | None = None) -> list[dict[str, Any]]:
        """Outgoing edges: [{source, target, relation, metadata}]."""
        self.load()
        return [dict(e) for e in self._out.get(node_id, []) if relation is None or e["relation"] == relation]

    def edges_to(self, node_id: str, relation: str | None = None) -> list[dict[str, Any]]:
        self.load()
        return [dict(e) for e in self._in.get(node_id, []) if relation is None or e["relation"] == relation]

    def exists(self, source: str, target: str, relation: str) -> dict[str, Any] | None:
        for e in self.edges_from(source, relation):
            if e["target"] == target:
                return e
        return None
