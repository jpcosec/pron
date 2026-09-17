"""Rebuilding a world's derived graph (spec 03, spec 11 §2): `stores update` on the stores
that may have moved, then kgdb's typed ingest into .pron/graph.nx.json. Library calls only;
kgdb and networkx are imported when a refresh runs, never at module load.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pron.kernel.ids import is_local
from pron.world.graph_file import GRAPH_RELPATH
from pron.world.store import Store


class GraphRefresher:
    """Writes the typed graph of one store (and the stores it links) to the world's .pron/."""

    def __init__(self, root: Path, store: Store) -> None:
        self.path = root / GRAPH_RELPATH
        self.store = store

    def __call__(
        self, exclude_tags: tuple[str, ...], stores: list[str] | None, light: bool
    ) -> dict[str, Any]:
        """The graph rebuilt and saved; returns kgdb's ingest report. `light` skips the
        stores update (the indexes of a write through sldb's own API are already current)."""
        from kgdb.ingest.typed import build_typed_snapshot

        if not light:
            self._update_stores(stores)
        snapshot, report = build_typed_snapshot(
            self.store.sp,
            self.store.pythonpath,
            exclude_tags,
            previous=self._previous_snapshot(),
        )
        self._save(snapshot)
        return report

    def _save(self, snapshot: Any) -> None:
        """The snapshot as kgdb's node-link JSON, through networkx."""
        import networkx as nx
        from kgdb.graph.utils import add_knowledge_node, save_graph

        g = nx.MultiDiGraph()
        for node in snapshot.nodes:
            add_knowledge_node(g, node)
        g.graph.update(snapshot.metadata)
        save_graph(g, self.path)

    def _update_stores(self, stores: list[str] | None) -> None:
        for s in stores if stores is not None else self.store.names():
            self.store.update_index(s)
        if stores is not None and not any(is_local(s) for s in stores):
            self.store.update_index()

    def _previous_snapshot(self):
        """`.pron/graph.nx.json` (kgdb's own node-link JSON, node `schema` holds the full
        KnowledgeNode dump — see `kgdb.graph.utils.add_knowledge_node`) read back as the
        GraphSnapshot `build_typed_snapshot`'s incremental path wants as `previous` (PLAN 15
        M4). Anything wrong with the file (missing, unparseable, foreign shape) is simply no
        previous: the next refresh falls back to a full rebuild, same as today."""
        if not self.path.exists():
            return None
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            from kgdb.contracts import GraphSnapshot, KnowledgeNode

            nodes = [
                KnowledgeNode.model_validate(n["schema"])
                for n in data.get("nodes", [])
                if n.get("schema")
            ]
            return GraphSnapshot(
                version="1.0", nodes=nodes, metadata=data.get("graph") or {}
            )
        except Exception:  # noqa: BLE001 - a previous snapshot is an optimization, never load-bearing
            return None
