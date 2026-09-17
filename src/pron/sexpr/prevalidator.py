"""Spec 11 §7: before the first write of a move, every write of the move is checked.

Coercion, state-machine transition, relation type, cardinality, condition and the sldb
roundtrip are all computed over an overlay — the payloads the earlier writes of the same
move would leave — so a move that would fail halfway fails before it touches anything.
The check raises StoreError; whatever the verbs verified on the way is put in the trace
and in the move's queries, whether the check passed or not.
"""

from __future__ import annotations

from typing import Any

from pron.kernel.part import Part
from pron.sexpr.collaborator import Collaborator


class Prevalidator(Collaborator):
    """The whole move simulated, and what the simulation verified."""

    def __call__(
        self,
        parts: list[Part],
        plans: list[dict[str, Any]],
        trace: list[str],
        record: dict[str, Any],
    ) -> None:
        overlay: dict[str, dict[str, Any]] = {}
        try:
            self.s._dry_parts(parts, plans, overlay)
        finally:
            self._notes(trace, record)

    def _notes(self, trace: list[str], record: dict[str, Any]) -> None:
        if self.s.kernel.notes:
            trace.extend("pre-validation: " + n for n in self.s.kernel.notes)
            record["queries"].extend(self.s.kernel.notes)
            self.s.kernel.notes = []
