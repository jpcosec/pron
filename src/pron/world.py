"""A world is an sldb store (spec 01). This module opens one, reads its declaration, and
refreshes its derived graph. Nothing here is knowledge of any particular world.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from sldb.cli.commands.store_update import update_store
from sldb.cli.model_utils import registered_model, resolve_model_ref
from sldb.store.ops import track_document

from pron.graph import GRAPH_RELPATH, Graph
from pron.ids import LOCAL, is_local
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
        self._graph = Graph(self.root)
        self._hash_mundo_cache: tuple[Any, str] | None = None
        self._pending: tuple[set[str] | None, bool] | None = None  # a deferred refresh: (stores, light)

    # -- declaration -----------------------------------------------------------

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

    def payload(
        self, model: str, name: str, store: str | None = LOCAL
    ) -> dict[str, Any]:
        """One document's payload, read straight from the store (spec 12 §3). Each read is
        its own sldb operation, so what the files say right now is what comes back, never
        what an earlier request of this World cached."""
        self.store.begin_operation()
        return self.store.payload(model, name, store)

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

    def hash_mundo(self) -> str:
        """Fingerprint of what the lexicon and the graph depend on: every model but the
        ledger (name, version, hash_b, schema), the predicates, and the linked stores.

        Memoized by (local hash_a, every linked store's own hash_a): hash_a is already the
        store's Merkle root over every model's hash_b, so it alone says whether anything in
        `idx.models` could have moved since the last call — a turn that reads this several
        times (spec 11 §5, §_move, §_refresh) recomputes the expensive part (per-model
        schema) once, not once per read (PLAN 15 M4)."""
        idx = self.store.store_index()
        key = (idx.hash_a, tuple(sorted((s.name, self._linked_hash_a(s.name)) for s in idx.stores)))
        cached = self._hash_mundo_cache
        if cached is not None and cached[0] == key:
            return cached[1]
        value = self._hash_mundo_uncached(idx)
        self._hash_mundo_cache = (key, value)
        return value

    def _linked_hash_a(self, name: str) -> str | None:
        try:
            return self.store.store_index(name).hash_a
        except Exception:  # noqa: BLE001 - a missing linked store counts as absent
            return None

    def _hash_mundo_uncached(self, idx: Any) -> str:
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
        for s in (
            idx.stores
        ):  # a linked store's models move the lexicon of a projection over it
            try:
                parts.append(
                    [
                        s.name,
                        sorted(
                            (m.name, self.store.models_index(m.name, s.name).hash_b)
                            for m in self.store.store_index(s.name).models
                        ),
                    ]
                )
            except Exception:  # noqa: BLE001 - a missing linked store counts as absent
                parts.append([s.name, None])
        return hashlib.sha256(
            json.dumps(parts, sort_keys=True, default=str).encode()
        ).hexdigest()

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

    def projection(self, name: str = "all", home: str | None = None) -> dict[str, Any]:
        """A ProjectionDoc payload; 'all' is synthesized when no document declares it. With
        `home`, the projection is read from that linked store and its 'local' means that
        store: a node's own projections work the same alone and through a daemon (12 §6)."""
        d = (
            self.store.doc("ProjectionDoc", f"projection-{name}", home)
            if "ProjectionDoc" in self.model_names(home)
            else None
        )
        if d is not None:
            return _rebind(dict(d.payload), home)
        if name != "all":
            raise StoreError(
                f"no projection named '{name}'"
                + (f" in store '{home}'" if not is_local(home) else "")
            )
        from pron.models.projection import ACTIONS

        return _rebind(
            {
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
            },
            home,
        )

    # -- derived graph -----------------------------------------------------------

    @property
    def graph(self) -> Graph:
        """The derived graph. A deferred refresh settles here first (spec 11 §8): every
        graph read — from Session code, from a World method, from the server's `graph` op —
        sees the graph of the writes already made, never one that predates them."""
        self.settle()
        return self._graph

    def graph_is_fresh(self) -> bool:
        return self.graph.is_fresh(self.model_hashes())

    @property
    def derived_dir(self) -> Path:
        """Where a consumer keeps what it derives from this world (vectors, indexes): .pron/,
        outside git like the graph (spec 11 §2)."""
        d = self.root / ".pron"
        d.mkdir(exist_ok=True)
        return d

    def is_ready(self) -> bool:
        """Whether this store is already a pron world. What that requires is pron's own
        business: a consumer asks, it does not check for a model by name."""
        names = set(self.model_names())
        required = {ref.split(":")[-1] for ref in PRON_MODELS} | {"RelationTypeDoc"}
        return required <= names

    def ensure_ready(self, template: str | Path | None = None) -> dict[str, Any] | None:
        """Make this store a world if it is not one yet, and leave its derived graph fresh.
        The one call a runtime makes on startup: it never decides what initialising a world
        involves, nor when the graph has to be rebuilt. Returns what init did, or None when
        the world was already there."""
        report = None
        if not self.is_ready():
            report = init_world(self.root, self.store.pythonpath, template=template)
            self.store.invalidate()
        self.refresh_if_stale()
        return report

    def refresh_if_stale(
        self, exclude_tags: tuple[str, ...] = ("type.pron.move",)
    ) -> bool:
        """Refresh only when the graph is missing or was built from other model hashes.
        Returns whether it refreshed."""
        if self.graph_is_fresh():
            return False
        self.refresh(exclude_tags)
        return True

    # -- deferred refresh (serve: respond, then settle) ----------------------------------

    def defer_refresh(self, stores: list[str] | None, light: bool) -> None:
        """Record a refresh to run after the response (spec 11 §8): the session answered
        first, and the graph catches up when the server settles or the next graph read
        arrives. Deferrals accumulate — the stores are their union, and the refresh is
        light only if every one of them was."""
        wanted = None if stores is None else set(stores)  # None: every store, as in refresh
        if self._pending is None:
            self._pending = (wanted, light)
        else:
            pending_stores, pending_light = self._pending
            union = None if pending_stores is None or wanted is None else pending_stores | wanted
            self._pending = (union, pending_light and light)

    @property
    def has_pending_refresh(self) -> bool:
        return self._pending is not None

    def settle(self) -> bool:
        """Run the pending refresh, if there is one, and say whether it ran. It only stops
        being pending after `refresh` returns: a refresh that raises stays pending, so a
        server that could not settle now retries on the next graph read."""
        if self._pending is None:
            return False
        stores, light = self._pending
        self._pending = None  # not pending while it runs: refresh reads self.graph itself
        try:
            self.refresh(stores=None if stores is None else sorted(stores), light=light)
            return True
        except Exception:
            self._pending = (stores, light)
            raise

    def refresh(
        self,
        exclude_tags: tuple[str, ...] = ("type.pron.move",),
        stores: list[str] | None = None,
        light: bool = False,
    ) -> dict[str, Any]:
        """stores update on the local store and on every store in `stores` (default: the
        linked ones too), then kgdb's typed ingest into .pron/graph.nx.json. Library calls
        only. kgdb and networkx are imported here, not at module load: a session that only
        reads never pays for them.

        `light` (PLAN 15 capa 8): skip stores update entirely — for the refresh right after
        a write that went through sldb's own API, whose indexes (hash_c/hash_d/hash_b/hash_a,
        semantic and sections shards for the documents it touched) are already current; a
        full `stores update` there would only re-read and re-hash every tracked file to catch
        a hand edit that cannot exist yet. The explicit `(refresh)` verb and `refresh_if_stale`
        keep the full path — the one that actually notices an edit made outside pron.

        A refresh here supersedes any pending deferral (spec 11 §8): it rebuilds the same
        graph from the same store, so the deferral is dropped and no later settle repeats it."""
        self._pending = None
        import networkx as nx
        from kgdb.graph.utils import add_knowledge_node, save_graph
        from kgdb.ingest.typed import build_typed_snapshot

        if not light:
            self._update_stores(stores)
        snapshot, report = build_typed_snapshot(
            self.store.sp, self.store.pythonpath, exclude_tags, previous=self._previous_snapshot()
        )
        g = nx.MultiDiGraph()
        for node in snapshot.nodes:
            add_knowledge_node(g, node)
        g.graph.update(snapshot.metadata)
        save_graph(g, self.root / GRAPH_RELPATH)
        self.graph.reload()
        self.store.invalidate()
        return report

    def _update_stores(self, stores: list[str] | None) -> None:
        for s in stores if stores is not None else self.stores():
            update_store(SimpleNamespace(store=str(self.store.sp_of(s)), pythonpath=self.store.pythonpath, wait=False, verbose=False))
        if stores is not None and not any(is_local(s) for s in stores):
            update_store(SimpleNamespace(store=str(self.store.sp), pythonpath=self.store.pythonpath, wait=False, verbose=False))

    def _previous_snapshot(self):
        """`.pron/graph.nx.json` (kgdb's own node-link JSON, node `schema` holds the full
        KnowledgeNode dump — see `kgdb.graph.utils.add_knowledge_node`) read back as the
        GraphSnapshot `build_typed_snapshot`'s incremental path wants as `previous` (PLAN 15
        M4). Anything wrong with the file (missing, unparseable, foreign shape) is simply no
        previous: the next refresh falls back to a full rebuild, same as today."""
        path = self.root / GRAPH_RELPATH
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            from kgdb.contracts import GraphSnapshot, KnowledgeNode

            nodes = [
                KnowledgeNode.model_validate(n["schema"])
                for n in data.get("nodes", [])
                if n.get("schema")
            ]
            return GraphSnapshot(version="1.0", nodes=nodes, metadata=data.get("graph") or {})
        except Exception:  # noqa: BLE001 - a previous snapshot is an optimization, never load-bearing
            return None


def _rebind(projection: dict[str, Any], home: str | None) -> dict[str, Any]:
    """A projection read from a linked store: its 'local' is that store."""
    if is_local(home):
        return projection
    projection["stores"] = [
        home if is_local(s) else s for s in (projection.get("stores") or ["local"])
    ]
    projection["home"] = home
    return projection


TEMPLATE_DIRS = {
    "anchors": ("AnchorDoc", "anchor-"),
    "projections": ("ProjectionDoc", "projection-"),
    "relations/types": ("RelationTypeDoc", "rt-"),
    "relations": ("RelationDoc", ""),
}


def apply_template(
    root: str | Path, template: str | Path, pythonpath: str | None = None
) -> list[str]:
    """Copy a world template into a world and track its documents (spec 01 §Plantilla):
    `anchors/*.md` as AnchorDoc, `projections/*.md` as ProjectionDoc, `relations/types/*.md`
    as RelationTypeDoc, `relations/*.md` as RelationDoc, each under <root>/knowledge/.
    A document whose name the world already has is left alone. Returns the export ids
    added."""
    import shutil

    root = Path(root).resolve()
    template = Path(template).resolve()
    store = Store(root, pythonpath)
    added: list[str] = []
    for sub, (model, prefix) in TEMPLATE_DIRS.items():
        src_dir = template / sub
        if not src_dir.is_dir() or model not in store.model_names():
            continue
        for src in sorted(src_dir.glob("*.md")):
            name = prefix + src.stem
            if store.doc(model, name) is not None:
                continue
            dst = root / "knowledge" / sub / src.name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            model_type, entry, idx = registered_model(store.sp, model, store.pythonpath)
            track_document(
                store.sp,
                store.project_root,
                idx,
                model_type,
                entry,
                dst,
                name,
                resolve_model_ref,
                store.pythonpath,
            )
            store.invalidate()
            added.append(f"{model}:{name}")
    if added:
        update_store(
            SimpleNamespace(
                store=str(store.sp),
                pythonpath=store.pythonpath,
                wait=False,
                verbose=False,
            )
        )
    return added


def init_world(
    root: str | Path,
    pythonpath: str | None = None,
    with_knowledge: bool = False,
    template: str | Path | None = None,
) -> dict[str, Any]:
    """Make a store a pron world: kgdb's typed relations plus pron's own models. With
    with_knowledge, also what pron's own knowledge base needs: SpecDoc and the relation
    type `implements` (a module or command implements a spec chapter). With a template,
    the world is born with the words, projections and relation types the template holds."""
    from kgdb.world import init_world as kgdb_init

    root = Path(root).resolve()
    store = Store(root, pythonpath)
    kgdb_report = kgdb_init(store.sp, store.pythonpath)
    added = [ref for ref in PRON_MODELS if store.register_model(ref)]
    if with_knowledge:
        for ref in (
            "pron.models:SpecDoc",
            "sldb.models.knowledge_surface:CliCommandDoc",
            "sldb.models.knowledge_surface:SurfaceDoc",
        ):
            if store.register_model(ref):
                added.append(ref)
    (root / LEDGER_DIR).mkdir(exist_ok=True)
    (root / ".pron").mkdir(exist_ok=True)
    gitignore = root / ".pron" / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("*\n", encoding="utf-8")
    types_added = _knowledge_relation_types(store) if with_knowledge else []
    # a model registered without documents leaves its index hash behind until the next update
    update_store(
        SimpleNamespace(
            store=str(store.sp), pythonpath=store.pythonpath, wait=False, verbose=False
        )
    )
    from_template = apply_template(root, template, pythonpath) if template else []
    return {
        "kgdb": kgdb_report.summary(),
        "pron_models_added": added,
        "relation_types_added": types_added,
        "template_added": from_template,
    }


KNOWLEDGE_RELATION_TYPES: list[dict[str, Any]] = [
    {
        "name": "implements",
        "axis": "HOW",
        "cardinality": "many_to_many",
        "source_types": ["SurfaceDoc", "CliCommandDoc"],
        "target_types": ["SpecDoc"],
        "description": "This module or command implements that chapter of the specification: the direct branch from the code to what it is supposed to do, derived from the spec references in the module's docstring.",
    },
]


def _knowledge_relation_types(store: Store) -> list[str]:
    """The relation types pron's own knowledge base uses, declared as documents."""
    added = []
    for rt in KNOWLEDGE_RELATION_TYPES:
        name = f"rt-{rt['name']}"
        if store.doc("RelationTypeDoc", name) is not None:
            continue
        payload = {"title": rt["name"], "direction": "directed", "condition": "", **rt}
        store.create(
            "RelationTypeDoc",
            name,
            payload,
            store.root / "knowledge" / "relations" / "types" / f"{rt['name']}.md",
        )
        added.append(rt["name"])
    return added
