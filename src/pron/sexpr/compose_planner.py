"""Planning a composition (spec 05, 06): every slot of every step resolved, and every
step's permission checked, before the first of them writes anything.

A compose alias is several writes said as one word ("book her a table"). Its steps name
their sides with slots, and a slot is either `$created` — what the composition itself makes,
which cannot be resolved because it does not exist yet — or a phrase of the sentence. The
projection has to allow every verb the steps do, or the whole composition is refused.
"""

from __future__ import annotations

from typing import Any

from pron.kernel.part import Part
from pron.kernel.response import Response
from pron.kernel.word import Word
from pron.sexpr.asker import Asker
from pron.sexpr.collaborator import Collaborator
from pron.sexpr.compose_slots import ComposeSlots
from pron.sexpr.phrase_planner import PhrasePlanner
from pron.sexpr.resolution import Resolution


class ComposePlanner(Collaborator):
    """A composition's steps, resolved; or the question or refusal that stops it."""

    def __call__(
        self,
        part: Part,
        trace: list[str],
        record: dict[str, Any],
        pending: dict[str, str] | None = None,
    ) -> dict[str, Any] | Response:
        assert part.verb is not None
        self.part, self.trace, self.record, self.pending = part, trace, record, pending
        self.slots = ComposeSlots(self.s)(part)
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
        res = PhrasePlanner(self.s)(np, model, self.trace, self.record, self.pending)
        if res.outcome == "ambiguo":
            return Asker(self.s).choice(self.part, slot_key, res, self.record)
        if res.outcome == "missing":
            return Asker(self.s).missing(res, self.record)
        return res

    # -- what this session lets a composition do (spec 05) -------------------------------

    def _permitted(self, word: Word) -> Response | None:
        steps = word.payload.get("steps", [])
        for verb in ("create", "change"):
            if not self.s.kernel.allowed(verb) and self._any_step(steps, verb):
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
        mode = self.s.lex.relation_types.get(relation, {}).get("mode", "read")
        return "assert" in mode

    @staticmethod
    def _any_step(steps: list[dict[str, Any]], verb: str) -> bool:
        return any(s.get("do") == verb for s in steps)
