"""Planning a composition (spec 05, 06): every slot of every step resolved, and every
step's permission checked, before the first of them writes anything.

A compose alias is several writes said as one word ("book her a table"). Its steps name
their sides with slots, and a slot is either `$created` — what the composition itself makes,
which cannot be resolved because it does not exist yet — or a phrase of the sentence. The
projection has to allow every verb the steps do, or the whole composition is refused.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.parts.part import Part
from pron.kernel.parts.response import Response
from pron.kernel.parts.word import Word
from pron.sexpr.dialogue.asker import Asker
from pron.sexpr.planning.compose_slots import ComposeSlots
from pron.sexpr.planning.phrase_planner import PhrasePlanner
from pron.sexpr.resolving.resolution import Resolution

if TYPE_CHECKING:
    from pron.sexpr.turn.move_context import MoveContext
    from pron.sexpr.turn.turn_tools import TurnTools


class ComposePlanner:
    """A composition's steps, resolved; or the question or refusal that stops it."""

    def __init__(self, tools: TurnTools):
        self.kernel, self.lex, self.world = tools.kernel, tools.lex, tools.world
        self.phrases = PhrasePlanner(tools.world, tools.lex, tools.dialogue)
        self.asker = Asker(tools.display, tools.dialogue)

    def __call__(self, part: Part, ctx: MoveContext) -> dict[str, Any] | Response:
        assert part.verb is not None
        self.part, self.ctx = part, ctx
        self.slots = ComposeSlots(self.world)(part)
        steps = self._steps(part.verb.payload.get("steps", []))
        if isinstance(steps, Response):
            return steps
        denied = self._permitted(part.verb)
        return denied if denied is not None else {"steps": steps}

    def _steps(self, steps: list[dict[str, Any]]) -> list[dict[str, Any]] | Response:
        """Every step's slots, in order; the first that cannot be resolved stops them all."""
        resolved_steps: list[dict[str, Any]] = []
        for step in steps:
            resolved = self._step(step)
            if isinstance(resolved, Response):
                return resolved
            resolved_steps.append(resolved)
        return resolved_steps

    def _step(self, step: dict[str, Any]) -> dict[str, Any] | Response:
        resolved: dict[str, Any] = {}
        for slot_key in ("source", "target"):
            res = self._slot(step.get(slot_key), slot_key)
            if isinstance(res, Response):
                return res
            if res is not None:
                resolved[slot_key] = res
        return resolved

    def _slot(self, slot: Any, slot_key: str) -> Resolution | Response | None:
        if not isinstance(slot, str) or not slot.startswith("$") or slot == "$created":
            return None
        kind, _, model = slot[1:].partition(":")
        if kind not in ("referent", "object"):
            return None
        np = self.slots.get(slot)
        if np is None:
            return Response(f"I need a {model.lower()} in that sentence.", "missing")
        return self._resolve(np, model, slot_key)

    def _resolve(self, np, model: str, slot_key: str) -> Resolution | Response:
        res = self.phrases(np, model, self.ctx)
        if res.outcome == "ambiguo":
            return self.asker.choice(self.part, slot_key, res, self.ctx)
        if res.outcome == "missing":
            return self.asker.missing(res, self.ctx)
        return res

    # -- what this session lets a composition do (spec 05) -------------------------------

    def _permitted(self, word: Word) -> Response | None:
        steps = word.payload.get("steps", [])
        for verb in ("create", "change"):
            if not self.kernel.allowed(verb) and self._any_step(steps, verb):
                return Response(f"In this session I cannot {verb}.", "missing")
        return self._assertable(steps)

    def _assertable(self, steps: list[dict[str, Any]]) -> Response | None:
        for s in steps:
            if s.get("do") == "assert" and not self._may_assert(s.get("relation")):
                return Response(
                    f"In this session I can tell you about {s.get('relation')}, not assert it.",
                    "missing",
                )
        return None

    def _may_assert(self, relation: Any) -> bool:
        mode = self.lex.relation_types.get(relation, {}).get("mode", "read")
        return "assert" in mode

    @staticmethod
    def _any_step(steps: list[dict[str, Any]], verb: str) -> bool:
        return any(s.get("do") == verb for s in steps)
