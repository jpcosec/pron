"""One load of a session's projection (spec 01, 05): the lexicon and what reads through it.

The projection is read from the session's home store; the first of its stores is where the
session writes. A read-only session sees the same projection with no actions and every
relation in mode read, so nothing said in it writes (spec 05). With an embedder, the
lexicon's vectors are cached per hash_mundo, home, projection and matcher.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pron.kernel.display import Display
from pron.kernel.ids import is_local
from pron.kernel.kernel import Kernel
from pron.sexpr.resolving.verbs import Verbs
from pron.surface.interpreter import Interpreter
from pron.world.lexicon import Lexicon
from pron.world.matching.matcher import Matcher
from pron.world.world import World


@dataclass(frozen=True)
class ProjectionSettings:
    """How a session reads its projection (spec 01, 05, 11 §8): fixed for its life."""

    name: str
    home: str | None
    read_only: bool
    defer_refresh: bool
    now: object


class ProjectionLoad:
    """The projection as loaded once, and everything built from it."""

    def __init__(
        self, world: World, settings: ProjectionSettings, matcher: Matcher, hash: str
    ):
        self.world, self.settings = world, settings
        self.projection = world.projection(settings.name, settings.home)
        stores = list(self.projection.get("stores") or ["local"])
        self.write_store: str | None = None if is_local(stores[0]) else stores[0]
        if settings.read_only:
            self.projection = self._read_only(stores)
        if matcher.embedder is not None:
            matcher.bind_cache(self._lexicon_cache(matcher, hash))
        self._build(matcher)

    def _build(self, matcher: Matcher) -> None:
        """What the projection gives the session: its lexicon and everything read through it."""
        self.lex = Lexicon(self.world, self.projection, matcher)
        self.interpreter = Interpreter(self.lex, now=self.settings.now)
        self.verbs = Verbs(self.lex)
        self.kernel = Kernel(self.verbs, self.projection)
        self.display = Display(self.world, self.projection, self.verbs)

    def _read_only(self, stores: list[str]) -> dict[str, Any]:
        """The projection with no actions and every relation in mode read (spec 05)."""
        names = [r["name"] for r in self.projection.get("relations") or []] or list(
            self.world.relation_types(stores)
        )
        return dict(
            self.projection,
            actions=[],
            relations=[{"name": n, "mode": "read"} for n in names],
        )

    def _lexicon_cache(self, matcher: Matcher, hash: str):
        return (
            self.world.root
            / ".pron"
            / f"lexicon.{hash}.{self.settings.home or 'local'}.{self.settings.name}.{matcher.id()}.json"
        )
