"""Planning one part of a move (spec 06, 13): every noun resolved before anything runs.

Nothing is written until every part of the move has been planned, so a move that cannot
be carried out whole is never carried out half. A part with no nouns — `(undo)`,
`(refresh)`, `(why)` — plans to nothing; a composition plans its steps; anything else
resolves the phrase in each role it has, against the class that role needs. A create's
subject is the exception: it does not exist yet, so there is nothing to resolve, only its
required fields to check.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.parts.part import Part
from pron.kernel.parts.response import Response
from pron.sexpr.dialogue.asker import Asker
from pron.sexpr.planning.compose_planner import ComposePlanner
from pron.sexpr.planning.needed_model import field_classes, needed_model
from pron.sexpr.planning.phrase_planner import PhrasePlanner
from pron.sexpr.resolving.resolution import Resolution

if TYPE_CHECKING:
    from pron.sexpr.turn.move_context import MoveContext
    from pron.sexpr.turn.turn_tools import TurnTools


class Planner:
    """A part's plan: what each of its roles resolved to, or the answer that stops it."""

    def __init__(self, tools: TurnTools):
        self.tools = tools
        self.phrases = PhrasePlanner(tools.world, tools.lex, tools.dialogue)
        self.asker = Asker(tools.display, tools.dialogue)

    def __call__(self, part: Part, ctx: MoveContext) -> dict[str, Any] | Response:
        if part.kind in ("undo", "refresh", "why"):
            return {}
        if part.kind == "compose":
            return ComposePlanner(self.tools)(part, ctx)
        plan = self._roles(part, ctx)
        if isinstance(plan, Response):
            return plan
        asked = self._create_data(part, ctx)
        return asked if asked is not None else plan

    def _roles(self, part: Part, ctx: MoveContext) -> dict[str, Any] | Response:
        """Subject first, then object: the first that cannot be resolved stops the part."""
        plan: dict[str, Any] = {}
        for role in ("subject", "object"):
            res = self._role(part, role, ctx)
            if isinstance(res, Response):
                return res
            if res is not None:
                plan[role] = res
        return plan

    def _role(
        self, part: Part, role: str, ctx: MoveContext
    ) -> Resolution | Response | None:
        np = getattr(part, role)
        if np is None or _is_new_subject(part, role):
            return None  # a create's subject does not exist yet: nothing to resolve
        need_model = needed_model(part, role, self.tools.lex)
        classes = None if need_model else field_classes(part, self.tools.lex)
        res = self.phrases(np, need_model, ctx, classes)
        if res.outcome == "ambiguo":
            return self.asker.choice(part, role, res, ctx)
        if res.outcome == "missing":
            return self.asker.missing(res, ctx)
        return res

    def _create_data(self, part: Part, ctx: MoveContext) -> Response | None:
        """A create the sentence left incomplete asks for the first field it still needs."""
        if not _is_new_subject(part, "subject"):
            return None
        assert part.subject is not None and part.subject.model is not None
        missing = self.tools.kernel.required_missing(
            part.subject.model, part.payload["fields"]
        )
        return self.asker.data(part, missing[0], ctx) if missing else None


def _is_new_subject(part: Part, role: str) -> bool:
    """The subject of a create: the document it names is the one it is about to make."""
    return (
        role == "subject"
        and part.kind == "action"
        and part.payload.get("verb") == "create"
    )
