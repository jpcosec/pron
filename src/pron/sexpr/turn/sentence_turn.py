"""What `Session.turn` does inside its move (spec 06, 13).

A sentence is one of three things. If a question is pending, it is the reply to it. If the
last turn was missing a value and this sentence is a fragment that fits that hole, it is a
correction of that turn, and the corrected sentence runs instead, as a move that says which
one it corrects. Otherwise it is a new sentence. Either way, the hole of the last missing
turn is used up: a correction can only follow the turn it corrects.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.parts.response import Response
from pron.sexpr.dialogue.corrector import Corrector
from pron.sexpr.dialogue.replier import Replier
from pron.sexpr.turn.new_sentence import NewSentence

if TYPE_CHECKING:
    from pron.sexpr.turn.move_context import MoveContext
    from pron.sexpr.turn.projection_state import ProjectionState


class SentenceTurn:
    """One sentence inside its move: the answer, and the move it refers to, if any."""

    def __init__(self, state: ProjectionState):
        self.state = state

    def __call__(self, sentence: str, ctx: MoveContext) -> tuple[Response, str]:
        tools = self.state.tools
        dialogue = tools.dialogue
        if dialogue.pending is not None:
            return Replier(self.state)(sentence, ctx)
        corrected = Corrector(tools.interpreter, tools.lex, dialogue)(sentence)
        hole = dialogue.last_missing
        dialogue.last_missing = None
        if corrected is None:
            return NewSentence(self.state)(sentence, ctx), ""
        return self._corrected(sentence, corrected, hole, ctx)

    def _corrected(
        self,
        sentence: str,
        corrected: str,
        hole: dict[str, Any] | None,
        ctx: MoveContext,
    ) -> tuple[Response, str]:
        assert hole is not None
        refers_to = hole.get("move_id", "")
        ctx.record["corrects"] = {
            "move": refers_to,
            "fragment": sentence,
            "sentence": corrected,
        }
        ctx.trace.append(f"correction of the last missing turn: {corrected!r}")
        return NewSentence(self.state)(corrected, ctx), refers_to
