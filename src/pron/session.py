"""A session: one world, one projection, one speaker, and the turn loop (spec 06, 07, 11).

turn(sentence): read hash_mundo → interpret → resolve → verify → decide → execute →
refresh if written → write the MoveDoc → answer. Everything the turn did is in the
trace; every trace line is a real call.

The session owns what outlives a turn — the world, the projection and what `_load` builds
from it, the dialogue, the ledger, the last hash_mundo it saw. Each phase of a turn is one
class in `pron.sexpr` that works over the session: a `Move` brackets the turn, an
`Evaluator` compiles, plans (`Planner`), pre-validates (`Prevalidator`) and executes
(`Executor`) the forms, and the dialogue side replies to pending questions (`Replier`) or
corrects the last missing turn (`Corrector`). The underscore methods below are the seams
those phases meet at, and the ones the surface's renderer asks.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pron.kernel.display import Display
from pron.kernel.ids import is_local
from pron.kernel.parts.item import Item
from pron.kernel.kernel import Kernel
from pron.kernel.parts.noun_phrase import NounPhrase
from pron.kernel.parts.part import Part
from pron.kernel.parts.response import Response  # noqa: F401 - re-exported: session.Response is the public name
from pron.sexpr.execution.compose_executor import ComposeExecutor
from pron.sexpr.planning.compose_slots import ComposeSlots
from pron.sexpr.dialogue.dialogue import Dialogue
from pron.sexpr.prevalidation.dry_runner import DryRunner
from pron.sexpr.turn.evaluator import Evaluator
from pron.sexpr.turn.form_turn import FormTurn
from pron.sexpr.turn.ledger import Ledger
from pron.sexpr.resolving.leftover_predicates import LeftoverPredicates
from pron.sexpr.turn.move import Body, Move
from pron.sexpr.turn.new_sentence import NewSentence
from pron.sexpr.planning.planner import Planner
from pron.sexpr.prevalidation.prevalidator import Prevalidator
from pron.sexpr.turn.sentence_turn import SentenceTurn
from pron.sexpr.dialogue.value_suggestions import ValueSuggestions
from pron.sexpr.resolving.verbs import Verbs
from pron.sexpr.execution.why_executor import WhyExecutor
from pron.surface.interpreter import Interpreter
from pron.world.matching.embedder_protocol import Embedder
from pron.world.lexicon import Lexicon
from pron.world.matching.matcher import Matcher
from pron.world.world import World


class Session:
    def __init__(
        self,
        world: World,
        projection: str = "all",
        speaker: str = "",
        speaker_address: str | None = None,
        now: str | datetime | None = None,
        embedder: Embedder | None = None,
        read_only: bool = False,
        home: str | None = None,
        defer_refresh: bool = False,
    ):
        """read_only: the projection's actions are dropped and every relation is in mode read, so
        nothing said in this session writes; the application decides that per session (spec 05).
        home: the linked store this session's world is (spec 01 §Un mundo en varios stores): its
        projections are read from there, its 'local' is that store, and that is where the session
        writes; None is the world's own store.
        defer_refresh (spec 11 §8): a write's graph refresh does not run in the turn; it is
        recorded on the world (World.defer_refresh) for whoever serves it. `pron serve` answers
        with the bytes and settles right after, still under its lock, so the next request reads a
        fresh graph; any graph read settles it too."""
        self.world = world
        self.projection_name = projection
        self.read_only = read_only
        self.defer_refresh = defer_refresh
        self.home = None if is_local(home) else home
        self.now = now
        self.dialogue = Dialogue(speaker=speaker, speaker_address=speaker_address)
        self.matcher = Matcher(embedder)
        self.hash = world.hash_mundo()
        self._load()
        self.ledger = Ledger(world, self.write_store)

    def _load(self) -> None:
        self.projection = self.world.projection(self.projection_name, self.home)
        stores = list(self.projection.get("stores") or ["local"])
        self.write_store: str | None = None if is_local(stores[0]) else stores[0]
        if self.read_only:
            self.projection = self._read_only(stores)
        if self.matcher.embedder is not None:
            self.matcher.bind_cache(self._lexicon_cache())
        self._build()

    def _build(self) -> None:
        """What the projection gives the session: its lexicon and everything read through it."""
        self.lex = Lexicon(self.world, self.projection, self.matcher)
        self.interpreter = Interpreter(self.lex, now=self.now)
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

    def _lexicon_cache(self):
        return (
            self.world.root
            / ".pron"
            / f"lexicon.{self.hash}.{self.home or 'local'}.{self.projection_name}.{self.matcher.id()}.json"
        )

    # -- the turn ---------------------------------------------------------------------------

    def turn(self, sentence: str) -> Response:
        """One sentence: the surface resolves it to forms (spec 13) and the forms are evaluated."""
        return self._move(
            sentence, lambda trace, record: SentenceTurn(self)(sentence, trace, record)
        )

    def eval(self, forms: str) -> Response:
        """One move written as forms (spec 13), with the same permissions, pre-validation, writes,
        refresh, MoveDoc and undo as a sentence. It never answers a pending question."""
        return self._move(
            forms, lambda trace, record: FormTurn(self)(forms, trace, record)
        )

    def _move(self, said: str, body: Body) -> Response:
        return Move(self)(said, body)

    def _sync(self, trace: list[str]) -> str:
        current = self.world.hash_mundo()
        if current != self.hash:
            trace.append(
                "the world changed outside pron: lexicon and projection reloaded"
            )
            self.hash = current
            self._load()
        return current

    def _refresh(self, trace: list[str], full: bool = False) -> None:
        """PLAN 15 capa 8: light (the default) — right after our own write, whose indexes
        sldb already kept current — skips `stores update` entirely; `full=True` is the
        explicit `(refresh)` verb's own path, the one that actually notices an edit made
        outside pron.

        With `defer_refresh` (spec 11 §8) the light refresh is recorded on the world instead
        of run here: the response leaves first and the settle runs right after, still under
        the server's lock, so the next request reads a fresh graph. `self.hash` still moves:
        hash_mundo reads the store, not the graph, and it is already current after the write.
        A full refresh stays synchronous: whoever asked for it wants the graph now."""
        if self.defer_refresh and not full:
            self.world.defer_refresh(stores=self.lex.stores, light=True)
            trace.append("graph refresh deferred until after the response")
            self.hash = self.world.hash_mundo()
            return
        report = self.world.refresh(stores=self.lex.stores, light=not full)
        trace.append(f"refresh: {report['nodes']} nodes, {report['edges']} edges")
        self.hash = self.world.hash_mundo()

    # -- the seams the phases meet at (pron.sexpr) ------------------------------------------

    def _new_sentence(
        self,
        sentence: str,
        trace: list[str],
        record: dict[str, Any],
        retry: bool = False,
    ) -> Response:
        return NewSentence(self)(sentence, trace, record, retry)

    def _eval(
        self,
        expr: Any,
        trace: list[str],
        record: dict[str, Any],
        retry: bool = False,
        again: Any = None,
    ) -> Response:
        return Evaluator(self)(expr, trace, record, retry, again)

    def _prevalidate(
        self,
        parts: list[Part],
        plans: list[dict[str, Any]],
        trace: list[str],
        record: dict[str, Any],
    ) -> None:
        """Spec 11 §7: every write of the move checked before the first one; see Prevalidator."""
        Prevalidator(self)(parts, plans, trace, record)

    def _dry_parts(
        self,
        parts: list[Part],
        plans: list[dict[str, Any]],
        overlay: dict[str, dict[str, Any]],
    ) -> None:
        DryRunner(self)(parts, plans, overlay)

    def _compose(
        self, part: Part, plan: dict[str, Any], trace: list[str], record: dict[str, Any]
    ) -> str:
        return ComposeExecutor(self)(part, plan, trace, record)

    def _value_word_suggestions(
        self, word: str, trace: list[str]
    ) -> list[tuple[str, str, str, str]]:
        return ValueSuggestions(self)(word, trace)

    # -- what the surface's renderer asks (surface/render.py) ---------------------------------

    def _needed_model(self, part: Part, role: str) -> str | None:
        return Planner(self).needed_model(part, role)

    def _compose_slots(self, part: Part) -> dict[str, NounPhrase]:
        return ComposeSlots(self)(part)

    def _leftover_predicates(self, np: NounPhrase, leftovers: list[Item]) -> list[str]:
        return LeftoverPredicates(self)(np, leftovers)

    def _why_target(self, part: Part) -> str | None:
        return WhyExecutor(self).target(part)
