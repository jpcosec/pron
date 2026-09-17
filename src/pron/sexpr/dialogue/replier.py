"""A sentence said while a question is pending (spec 06): an answer, or not.

It may be a new order, and then the question is dropped and the order runs; it may call the
whole thing off; or it answers — the value of the field a create was missing, or which of
the candidates was meant. An answer fills the hole in the part that asked, and that part is
said again as forms and evaluated like any other move. An answer that picks none, or more
than one, leaves the question pending and asks it again.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pron.kernel.ids import doc_of
from pron.kernel.parts.part import Part
from pron.kernel.parts.response import Response
from pron.sexpr.execution.listing import numbered
from pron.sexpr.dialogue.pending import Pending
from pron.sexpr.resolving.resolution import address_to_export_id
from pron.sexpr.turn.evaluator import Evaluator
from pron.sexpr.turn.new_sentence import NewSentence
from pron.surface.render import said

if TYPE_CHECKING:
    from pron.sexpr.turn.move_context import MoveContext
    from pron.sexpr.turn.projection_state import ProjectionState


class Replier:
    """The reply to a pending question, and the move it refers to."""

    def __init__(self, state: ProjectionState):
        self.state, self.tools = state, state.tools
        self.dialogue = self.tools.dialogue

    def __call__(self, sentence: str, ctx: MoveContext) -> tuple[Response, str]:
        pending = self.dialogue.pending
        assert pending is not None
        if self._is_order(sentence):
            return self._order(sentence, pending, ctx), pending.move_id
        if sentence.strip().lower().rstrip("?.! ") in ("none", "neither", "no"):
            self.dialogue.close()
            return Response("Cancelled.", "unico"), pending.move_id
        return self._answer(pending, sentence, ctx), pending.move_id

    def _answer(self, pending: Pending, sentence: str, ctx: MoveContext) -> Response:
        """The value of the missing field, or which of the candidates was meant."""
        part: Part = pending.state["part"]
        if pending.kind == "data":
            return self._data(part, pending, sentence, ctx)
        return self._choice(part, pending, sentence, ctx)

    def _is_order(self, sentence: str) -> bool:
        interp = self.tools.interpreter.interpret(sentence)
        kinds = [w.kind for i in interp.items for w in i.words]
        return self.dialogue.classify_reply(sentence, kinds) == "order"

    def _order(self, sentence: str, pending: Pending, ctx: MoveContext) -> Response:
        ctx.trace.append("pending dropped: a new order")
        self.dialogue.close()
        ctx.record["dropped_pending"] = pending.sentence
        return NewSentence(self.state)(sentence, ctx)

    def _data(
        self, part: Part, pending: Pending, sentence: str, ctx: MoveContext
    ) -> Response:
        value = sentence.strip()
        part.payload["fields"][pending.field_name] = value
        self.dialogue.close()
        ctx.trace.append(
            f"{pending.field_name} = {value!r} (answer to the pending question)"
        )
        return self._resume(part, ctx)

    def _choice(
        self, part: Part, pending: Pending, sentence: str, ctx: MoveContext
    ) -> Response:
        picks = self.dialogue.pick(sentence, self.tools.matcher)
        if len(picks) != 1:
            listing = numbered(pending.labels)
            return Response(f"Still pending. Which one? {listing}", "ambiguo")
        chosen = pending.candidates[picks[0]]
        ctx.trace.append(f"'{sentence.strip()}' → {chosen} (answer to the pending question)")
        self.dialogue.close()
        _pin(getattr(part, pending.slot, None), chosen)
        return self._resume(part, ctx)

    def _resume(self, part: Part, ctx: MoveContext) -> Response:
        """The answer filled the hole: the part is said again as forms and evaluated."""
        return Evaluator(self.state)(said([part], self.tools), ctx)


def _pin(np, chosen: str) -> None:
    """The phrase that was ambiguous now names exactly the document that was chosen."""
    if np is not None:
        np.proper = []
        np.predicates = [f'doc ~ "^{doc_of(address_to_export_id(chosen))}$"']
