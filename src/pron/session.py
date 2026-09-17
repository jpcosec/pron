"""A session: one world, one projection, one speaker, and the turn loop (spec 06, 07, 11).

turn(sentence): read hash_mundo → interpret → resolve → verify → decide → execute →
refresh if written → write the MoveDoc → answer. Everything the turn did is in the
trace; every trace line is a real call.

The session is where a turn's parts are put together, and it owns what outlives a turn: the
dialogue, the matcher, and the `ProjectionState` — the projection as last loaded, the
hash_mundo it was loaded at, the ledger. Each move gets a `MoveContext` of its own, and the
phases in `pron.sexpr` work over that context and that state: a `Move` brackets the turn, a
`SentenceTurn` or `FormTurn` is its body, and an `Evaluator` compiles, plans, pre-validates
and executes the forms, understanding them again itself if the world moves meanwhile. No
phase calls back into the session.
"""

from __future__ import annotations

from datetime import datetime

from pron.kernel.ids import is_local
from pron.kernel.parts.response import Response  # noqa: F401 - re-exported: session.Response is the public name
from pron.sexpr.dialogue.dialogue import Dialogue
from pron.sexpr.turn.form_turn import FormTurn
from pron.sexpr.turn.move import Body, Move
from pron.sexpr.turn.move_context import MoveContext
from pron.sexpr.turn.projection_load import ProjectionSettings
from pron.sexpr.turn.projection_state import ProjectionState
from pron.sexpr.turn.sentence_turn import SentenceTurn
from pron.world.matching.embedder_protocol import Embedder
from pron.world.matching.matcher import Matcher
from pron.world.world import World


def _loaded(name: str) -> property:
    """What the projection last loaded for this session (read-only)."""
    return property(lambda self: getattr(self.state.loaded, name))


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
        home = None if is_local(home) else home
        settings = ProjectionSettings(projection, home, read_only, defer_refresh, now)
        self.dialogue = Dialogue(speaker=speaker, speaker_address=speaker_address)
        self.matcher = Matcher(embedder)
        self.state = ProjectionState(world, settings, self.matcher, self.dialogue)
        self.ledger = self.state.ledger
        self._said = ""  # the sentence the last move said; a pending question refers to it

    projection = _loaded("projection")
    write_store = _loaded("write_store")
    lex = _loaded("lex")
    interpreter = _loaded("interpreter")
    verbs = _loaded("verbs")
    kernel = _loaded("kernel")
    display = _loaded("display")

    @property
    def hash(self) -> str:
        return self.state.hash

    def turn(self, sentence: str) -> Response:
        """One sentence: the surface resolves it to forms (spec 13) and the forms are evaluated."""
        return self._move(
            sentence, lambda ctx: SentenceTurn(self.state)(sentence, ctx)
        )

    def eval(self, forms: str) -> Response:
        """One move written as forms (spec 13), with the same permissions, pre-validation, writes,
        refresh, MoveDoc and undo as a sentence. It never answers a pending question."""
        return self._move(forms, lambda ctx: FormTurn(self.state)(forms, ctx))

    def _move(self, said: str, body: Body) -> Response:
        """A move of its own context, which starts from the sentence the last one said."""
        ctx = MoveContext(sentence=self._said)
        try:
            return Move(self.state)(said, ctx, body)
        finally:
            self._said = ctx.sentence
