"""The projection a session last loaded, and the hash_mundo it was loaded at (spec 05, 11).

A session reads through one projection of one world. What that projection builds — its
lexicon and everything read through it — is only good while the world is the one it was
built from, so this is where hash_mundo is kept: read again when a move opens (`sync`) and
just before it executes (`reload`, spec 11 §5), moved forward after the session's own writes
(`refresh`, PLAN 15 capa 8 and spec 11 §8), and where the projection is loaded again when
it moved. The phases never reload anything themselves: they ask this, and take `tools` again.
"""

from __future__ import annotations

from pron.sexpr.dialogue.dialogue import Dialogue
from pron.sexpr.turn.ledger import Ledger
from pron.sexpr.turn.projection_load import ProjectionLoad, ProjectionSettings
from pron.sexpr.turn.turn_tools import TurnTools
from pron.world.matching.matcher import Matcher
from pron.world.world import World

OUTSIDE = "the world changed outside pron: lexicon and projection reloaded"
RELOADED = "the world changed while understanding: lexicon and projection reloaded, understanding again"


class ProjectionState:
    """The loaded projection, the hash it was loaded at, and the ledger of the session."""

    def __init__(
        self, world: World, settings: ProjectionSettings, matcher: Matcher, dialogue: Dialogue
    ):
        self.world, self.settings = world, settings
        self.matcher, self.dialogue = matcher, dialogue
        self.hash = world.hash_mundo()
        self.load()
        self.ledger = Ledger(world, self.loaded.write_store)

    def load(self) -> None:
        self.loaded = ProjectionLoad(self.world, self.settings, self.matcher, self.hash)

    @property
    def tools(self) -> TurnTools:
        """The pieces a move works with, as of the last load."""
        loaded = self.loaded
        return TurnTools(
            world=self.world,
            matcher=self.matcher,
            dialogue=self.dialogue,
            ledger=self.ledger,
            projection=loaded.projection,
            write_store=loaded.write_store,
            lex=loaded.lex,
            interpreter=loaded.interpreter,
            verbs=loaded.verbs,
            kernel=loaded.kernel,
            display=loaded.display,
        )

    def sync(self, trace: list[str]) -> str:
        """hash_mundo as a move opens; the projection loaded again if it moved outside pron."""
        current = self.world.hash_mundo()
        if current != self.hash:
            trace.append(OUTSIDE)
            self.hash = current
            self.load()
        return current

    def reload(self, current: str, trace: list[str]) -> None:
        """The world moved while a move was understood: the projection as it is now."""
        trace.append(RELOADED)
        self.hash = current
        self.load()

    def refresh(self, trace: list[str], full: bool = False) -> None:
        """PLAN 15 capa 8: light (the default) — right after our own write, whose indexes
        sldb already kept current — skips `stores update` entirely; `full=True` is the
        explicit `(refresh)` verb's own path, the one that actually notices an edit made
        outside pron.

        With `defer_refresh` (spec 11 §8) the light refresh is recorded on the world instead
        of run here: the response leaves first and the settle runs right after, still under
        the server's lock, so the next request reads a fresh graph. `hash` still moves:
        hash_mundo reads the store, not the graph, and it is already current after the write.
        A full refresh stays synchronous: whoever asked for it wants the graph now."""
        stores = self.loaded.lex.stores
        if self.settings.defer_refresh and not full:
            self.world.defer_refresh(stores=stores, light=True)
            trace.append("graph refresh deferred until after the response")
        else:
            report = self.world.refresh(stores=stores, light=not full)
            trace.append(f"refresh: {report['nodes']} nodes, {report['edges']} edges")
        self.hash = self.world.hash_mundo()
