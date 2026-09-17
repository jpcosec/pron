"""Simulating an action part (spec 11 §7): what it would write, without writing it.

The projection has to allow the verb. A create is simulated whole and, when the form gave
it a name, the payload it would leave goes into the overlay under that name, so a later
part of the same move that names it sees it. Every other verb is its own `Verb.dry`
(kernel/actions/verb.py): the one place that verb's semantics live.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.ids import join_id
from pron.kernel.parts.part import Part
from pron.sexpr.prevalidation.action_verb import action_verb
from pron.world.store_error import StoreError

if TYPE_CHECKING:
    from pron.kernel.kernel import Kernel


class DryAction:
    """One action part, simulated over the overlay the move has built so far."""

    def __init__(self, kernel: Kernel, write_store: str | None):
        self.kernel, self.write_store = kernel, write_store

    def __call__(
        self,
        part: Part,
        plan: dict[str, Any],
        overlay: dict[str, dict[str, Any]],
    ) -> None:
        verb = action_verb(part)
        if verb is None or not self.kernel.allowed(verb):
            raise StoreError(f"in this session I cannot {verb}")
        if verb == "create":
            self._create(part, overlay)
        else:
            self._writes(verb, part, plan, overlay)

    def _create(self, part: Part, overlay: dict[str, dict[str, Any]]) -> None:
        assert part.subject is not None and part.subject.model is not None
        full = self.kernel.dry_create(
            part.subject.model, part.payload["fields"], overlay
        )
        if part.payload.get("name"):
            overlay[self._named(part)] = full

    def _named(self, part: Part) -> str:
        assert part.subject is not None and part.subject.model is not None
        return join_id(self.write_store, part.subject.model, part.payload["name"])

    def _writes(
        self,
        verb: str,
        part: Part,
        plan: dict[str, Any],
        overlay: dict[str, dict[str, Any]],
    ) -> None:
        for e in plan["subject"].export_ids():
            self.kernel.dry_run(verb, e, part.field_name, part.value, overlay)
