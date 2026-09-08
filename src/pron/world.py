"""A world is an sldb store. This module opens one, reads its declaration, and
refreshes its derived graph. Nothing here is knowledge of any particular world.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import networkx as nx

from kgdb.graph.utils import add_knowledge_node, save_graph
from kgdb.ingest.typed import build_typed_snapshot
from kgdb.world import init_world as kgdb_init
from sldb.cli.commands.store_update import update_store

from pron.graph import GRAPH_RELPATH, Graph
from pron.store import Store, StoreError

PRON_MODELS = (
    "pron.models:AnchorDoc",
    "pron.models:ProjectionDoc",
    "pron.models:MoveDoc",
)
LEDGER_MODEL = "MoveDoc"
LEDGER_DIR = Path("ledger")
PROJECTIONS_DIR = Path("knowledge") / "projections"


class World:
    """One store, opened for reading its declaration and refreshing its graph."""

    def __init__(self, root: str | Path, pythonpath: str | None = None) -> None:
        self.root = Path(root).resolve()
        self.store = Store(self.root, pythonpath)
        self.graph = Graph(self.root)

    # -- declaration -----------------------------------------------------------

    def model_names(self) -> list[str]:
        return self.store.model_names()

    def model_hashes(self) -> dict[str, str]:
        return {m.name: self.store.models_index(m.name).hash_b for m in self.store.store_index().models}

    def base_models(self, name: str) -> list[str]:
        try:
            return list(self.store.models_index(name).base_models)
        except StoreError:
            return []

    def family_of(self, name: str) -> list[str]:
        """The model and its bases, nearest first."""
        return [name, *self.base_models(name)]

    def hash_mundo(self) -> str:
        """Fingerprint of what the lexicon and the graph depend on: every model but the
        ledger (name, version, hash_b, schema), the predicates, and the linked stores."""
        idx = self.store.store_index()
        parts: list[Any] = []
        for m in sorted(idx.models, key=lambda m: m.name):
            if m.name == LEDGER_MODEL:
                continue
            mi = self.store.models_index(m.name)
            try:
                schema = self.store.schema(m.name)
            except Exception:  # noqa: BLE001 - an unresolvable model still counts by its hash
                schema = []
            parts.append([m.name, mi.version, mi.hash_b, schema])
        parts.append(sorted((p.name, p.axis) for p in idx.predicates))
        parts.append(sorted((s.name, s.path) for s in idx.stores))
        return hashlib.sha256(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()

    def relation_types(self) -> dict[str, dict[str, Any]]:
        """name -> RelationTypeDoc payload, read by address from the store."""
        if "RelationTypeDoc" not in self.model_names():
            return {}
        return {d.payload["name"]: dict(d.payload, doc=d.name) for d in self.store.docs_of("RelationTypeDoc")}

    def projection(self, name: str = "all") -> dict[str, Any]:
        """A ProjectionDoc payload; 'all' is synthesized when no document declares it."""
        d = self.store.doc("ProjectionDoc", f"projection-{name}") if "ProjectionDoc" in self.model_names() else None
        if d is not None:
            return dict(d.payload)
        if name != "all":
            raise StoreError(f"no projection named '{name}'")
        from pron.models.projection import ACTIONS
        return {"name": "all", "stores": ["local"], "models": [], "relations": [], "actions": list(ACTIONS),
                "aliases": ["all"], "naming": {}, "display": {}, "key": {}, "matching": {"neighbors": 3, "threshold": 0.55}, "description": ""}

    # -- derived graph -----------------------------------------------------------

    def graph_is_fresh(self) -> bool:
        return self.graph.is_fresh(self.model_hashes())

    def refresh(self, exclude_tags: tuple[str, ...] = ("type.pron.move",)) -> dict[str, Any]:
        """stores update, then kgdb's typed ingest into .pron/graph.nx.json. Library calls only."""
        update_store(SimpleNamespace(store=str(self.store.sp), pythonpath=self.store.pythonpath, wait=False, verbose=False))
        snapshot, report = build_typed_snapshot(self.store.sp, self.store.pythonpath, exclude_tags)
        g = nx.MultiDiGraph()
        for node in snapshot.nodes:
            add_knowledge_node(g, node)
        g.graph.update(snapshot.metadata)
        save_graph(g, self.root / GRAPH_RELPATH)
        self.graph.reload()
        self.store.invalidate()
        return report


def init_world(root: str | Path, pythonpath: str | None = None, with_atoms: bool = False) -> dict[str, Any]:
    """Make a store a pron world: kgdb's typed relations plus pron's own models."""
    root = Path(root).resolve()
    store = Store(root, pythonpath)
    kgdb_report = kgdb_init(store.sp, store.pythonpath)
    added = [ref for ref in PRON_MODELS if store.register_model(ref)]
    if with_atoms and store.register_model("pron.models:Atom"):
        added.append("pron.models:Atom")
    (root / LEDGER_DIR).mkdir(exist_ok=True)
    (root / ".pron").mkdir(exist_ok=True)
    gitignore = root / ".pron" / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("*\n", encoding="utf-8")
    return {"kgdb": kgdb_report.summary(), "pron_models_added": added}
