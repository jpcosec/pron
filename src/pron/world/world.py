"""A world is an sldb store (spec 01). This module opens one, reads its declaration, and
refreshes its derived graph. Nothing here is knowledge of any particular world.

What a World does is spread over pron.world: its declaration (`WorldDeclaration`), its
fingerprint (`WorldFingerprint`), its projections (`ProjectionReader`), its typed graph
(`Graph`, sldb's own edge index) and the refresh deferred past a response
(`PendingRefresh`); making a store a world is `WorldInit` and `WorldTemplate`, reached
through `init_world` and `apply_template`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sldb.api import rebuild_edges

from pron.kernel.ids import LOCAL, is_local
from pron.world.fingerprint import WorldFingerprint
from pron.world.graph import Graph
from pron.world.pending_refresh import PendingRefresh
from pron.world.projection_reader import ProjectionReader
from pron.world.store import Store
from pron.world.world_declaration import WorldDeclaration
from pron.world.world_init import LEDGER_DIR, PRON_MODELS, init_world  # noqa: F401 - LEDGER_DIR is read from here
from pron.world.world_template import apply_template  # noqa: F401 - the template door, from here too


class World(WorldDeclaration):
    """One store, opened for reading its declaration and refreshing its graph."""

    def __init__(self, root: str | Path, pythonpath: str | None = None) -> None:
        self.root = Path(root).resolve()
        super().__init__(Store(self.root, pythonpath))
        self._graph = Graph(self.store.sp)
        self._fingerprint = WorldFingerprint(self.store)
        self._pending = PendingRefresh()
        self._projections = ProjectionReader(self.store)

    # -- documents, fingerprint and projections --------------------------------

    def payload(
        self, model: str, name: str, store: str | None = LOCAL
    ) -> dict[str, Any]:
        """One document's payload, read straight from the store (spec 12 §3). Each read is
        its own sldb operation, so what the files say right now is what comes back, never
        what an earlier request of this World cached."""
        self.store.begin_operation()
        return self.store.payload(model, name, store)

    def hash_mundo(self) -> str:
        """Fingerprint of what the lexicon and the graph depend on: every model but the
        ledger (name, version, hash_b, schema), the predicates, and the linked stores,
        memoized by the stores' own hash_a (spec 11 §5, PLAN 15 M4)."""
        return self._fingerprint()

    def projection(self, name: str = "all", home: str | None = None) -> dict[str, Any]:
        """A ProjectionDoc payload; 'all' is synthesized when no document declares it. With
        `home`, the projection is read from that linked store and its 'local' means that
        store: a node's own projections work the same alone and through a daemon (12 §6)."""
        return self._projections(name, home)

    # -- derived graph -----------------------------------------------------------

    @property
    def graph(self) -> Graph:
        """The derived graph. A deferred refresh settles here first (spec 11 §8): every
        graph read — from Session code, from a World method, from the server's `graph` op —
        sees the graph of the writes already made, never one that predates them."""
        self.settle()
        return self._graph

    def graph_is_fresh(self) -> bool:
        return not self.graph.stale

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

    def refresh_if_stale(self) -> bool:
        """Refresh only when sldb reports a document whose shard is missing or out of hash
        (a write made outside sldb). Returns whether it refreshed."""
        if self.graph_is_fresh():
            return False
        self.refresh()
        return True

    # -- deferred refresh (serve: respond, then settle) ----------------------------------

    def defer_refresh(self, stores: list[str] | None, light: bool) -> None:
        """Record a refresh to run after the response (spec 11 §8): the session answered
        first, and the graph catches up when the server settles or the next graph read
        arrives. Deferrals accumulate — the stores are their union, and the refresh is
        light only if every one of them was."""
        self._pending.defer(stores, light)

    @property
    def has_pending_refresh(self) -> bool:
        return self._pending.is_pending

    def settle(self) -> bool:
        """Run the pending refresh, if there is one, and say whether it ran. It only stops
        being pending after `refresh` returns: a refresh that raises stays pending, so a
        server that could not settle now retries on the next graph read."""
        return self._pending.settle(self.refresh)

    def refresh(
        self,
        stores: list[str] | None = None,
        light: bool = False,
    ) -> dict[str, Any]:
        """stores update on the local store and on every store in `stores` (default: the
        linked ones too), then `sldb.api.rebuild_edges` brings the edge index current.
        Library calls only.

        `light` (PLAN 15 capa 8): skip stores update entirely — for the refresh right after
        a write that went through sldb's own API, whose indexes (hash_c/hash_d/hash_b/hash_a,
        semantic, sections and edges shards for the documents it touched) are already
        current: `rebuild_edges` there finds nothing to do. A full `stores update` there
        would only re-read and re-hash every tracked file to catch a hand edit that cannot
        exist yet. The explicit `(refresh)` verb and `refresh_if_stale` keep the full path —
        the one that actually notices an edit made outside pron.

        A refresh here supersedes any pending deferral (spec 11 §8): it brings the same
        index of the same store current, so the deferral is dropped and no later settle
        repeats it."""
        self._pending.clear()
        if not light:
            self._update_stores(stores)
        report = rebuild_edges(self.store.sp, self.store.pythonpath)
        self.graph.reload()
        self.store.invalidate()
        return report.model_dump()

    def _update_stores(self, stores: list[str] | None) -> None:
        for s in stores if stores is not None else self.store.names():
            self.store.update_index(s)
        if stores is not None and not any(is_local(s) for s in stores):
            self.store.update_index()
