"""Spec 11 §7: before the first write of a move, every write of the move is checked.

Coercion, state-machine transition, relation type, cardinality, condition and the sldb
roundtrip are all computed over an overlay — the payloads the earlier writes of the same
move would leave — so a move that would fail halfway fails before it touches anything.
The check raises StoreError; whatever the verbs verified on the way is put in the trace
and in the move's queries, whether the check passed or not.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.parts.part import Part
from pron.sexpr.prevalidation.dry_runner import DryRunner

if TYPE_CHECKING:
    from pron.kernel.kernel import Kernel
    from pron.sexpr.turn.move_context import MoveContext


class Prevalidator:
    """The whole move simulated, and what the simulation verified."""

    def __init__(self, kernel: Kernel, dry_runner: DryRunner):
        self.kernel, self.dry_runner = kernel, dry_runner

    def __call__(
        self, parts: list[Part], plans: list[dict[str, Any]], ctx: MoveContext
    ) -> None:
        overlay: dict[str, dict[str, Any]] = {}
        try:
            self.dry_runner(parts, plans, overlay)
        finally:
            self._notes(ctx)

    def _notes(self, ctx: MoveContext) -> None:
        if self.kernel.notes:
            ctx.trace.extend("pre-validation: " + n for n in self.kernel.notes)
            ctx.record["queries"].extend(self.kernel.notes)
            self.kernel.notes = []
