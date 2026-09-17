"""A new sentence (spec 13, 05): the surface says it as forms and the forms are evaluated.

The surface only interprets. A sentence made only of words the projection does not have,
or of nouns among them, is answered with what the lexicon has near it; a sentence with any
part nobody could parse is answered with sentences this world does understand. Anything
else is said as forms, and the forms are what gets resolved and run — so a sentence and the
forms it says leave exactly the same move. If the world changes while the move is being
understood, the sentence itself is understood again, not the forms it said the first time.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pron.kernel.parts.interpretation import Interpretation
from pron.kernel.parts.response import Response
from pron.sexpr.dialogue.parse_hint import cannot_parse_hint
from pron.sexpr.dialogue.unknown_words import UnknownWords
from pron.sexpr.dialogue.value_suggestions import ValueSuggestions
from pron.sexpr.turn.evaluator import Evaluator
from pron.surface.render import said

if TYPE_CHECKING:
    from pron.sexpr.turn.move_context import MoveContext
    from pron.sexpr.turn.projection_state import ProjectionState


class NewSentence:
    """One sentence that does not answer a pending question, understood and run."""

    def __init__(self, state: ProjectionState):
        self.state, self.tools = state, state.tools

    def __call__(self, sentence: str, ctx: MoveContext) -> Response:
        ctx.sentence = sentence
        interp = self.tools.interpreter.interpret(sentence)
        ctx.record["interpretation"] = interp.to_record()
        ctx.trace.append("interpretation: " + interp.forma)
        unclear = self._unclear(interp, ctx)
        if unclear is not None:
            return unclear
        return self._evaluate(sentence, interp, ctx)

    def _evaluate(
        self, sentence: str, interp: Interpretation, ctx: MoveContext
    ) -> Response:
        """The forms the sentence says; if the world moves meanwhile, the sentence again,
        over the projection as it was loaded again."""
        return Evaluator(self.state)(
            said(interp.parts, self.tools),
            ctx,
            again=lambda: NewSentence(self.state)(sentence, ctx),
        )

    def _unclear(self, interp: Interpretation, ctx: MoveContext) -> Response | None:
        t = self.tools
        if interp.unknown and all(p.kind in ("none", "nominal") for p in interp.parts):
            suggestions = ValueSuggestions(t.projection, t.lex, t.world, t.matcher)
            return UnknownWords(t.lex, t.matcher, suggestions)(interp, ctx)
        if any(p.kind == "none" for p in interp.parts):
            return Response(cannot_parse_hint(t.lex), "missing")
        return None
