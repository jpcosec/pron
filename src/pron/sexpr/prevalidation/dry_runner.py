"""Spec 11 §7: the parts of a move dispatched to their simulation, one kind each.

Only the parts that would write are simulated — an action, an assert, a composition, and
`undo`, which needs its permission checked like any other write. A read or a nominal
answer writes nothing, so there is nothing to check before it. The overlay is threaded
through every part in order, so each one is simulated over what the earlier ones would
have left.
"""

from __future__ import annotations

from typing import Any

from pron.kernel.parts.part import Part
from pron.sexpr.turn.collaborator import Collaborator
from pron.sexpr.prevalidation.dry_action import DryAction
from pron.sexpr.prevalidation.dry_assert import DryAssert
from pron.sexpr.prevalidation.dry_compose import DryCompose
from pron.world.store_error import StoreError


class DryRunner(Collaborator):
    """part.kind → the simulation for that kind of part."""

    def __call__(
        self,
        parts: list[Part],
        plans: list[dict[str, Any]],
        overlay: dict[str, dict[str, Any]],
    ) -> None:
        for part, plan in zip(parts, plans):
            fn = getattr(self, "_d_" + part.kind, None)
            if fn is not None:
                fn(part, plan, overlay)

    def _d_action(self, part, plan, overlay) -> None:
        DryAction(self.s)(part, plan, overlay)

    def _d_assert(self, part, plan, overlay) -> None:
        assert part.verb is not None and part.verb.relation is not None
        DryAssert(self.s)(
            part.verb.relation,
            plan["subject"].export_ids(),
            plan["object"].export_ids(),
            overlay,
        )

    def _d_compose(self, part, plan, overlay) -> None:
        DryCompose(self.s)(part, plan, overlay)

    def _d_undo(self, part, plan, overlay) -> None:
        if not self.s.kernel.allowed("undo"):
            raise StoreError("in this session I cannot undo")
