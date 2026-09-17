"""Pre-validation of a move (spec 11 §7): what a write would leave, without writing. Each
step mutates a JSON-safe copy of the payload — the move's own overlay when an earlier step
already touched the document — and sldb round-trips it before it joins the overlay, so the
next step of the move sees it.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from pron.kernel.actions.verb_registry import VERBS
from pron.kernel.ids import model_of, store_of

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.kernel.kernel import Kernel


class DryRun:
    """The dry runs of one kernel's verbs over a move's overlay."""

    def __init__(self, kernel: "Kernel") -> None:
        self.kernel = kernel

    def __call__(
        self,
        verb: str,
        export_id: str,
        field_name: str | None,
        value: Any,
        overlay: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """A verb outside the registry (none in practice: `_action` rejects it at execution)
        leaves the payload untouched but still round-tripped."""
        v = VERBS.get(verb)
        if v is None:
            model = model_of(export_id)
            p = self.load(export_id, overlay)
            return self.save(export_id, model, p, overlay)
        return v.dry(self.kernel, export_id, field_name, value, overlay)

    def load(
        self, export_id: str, overlay: dict[str, dict[str, Any]]
    ) -> dict[str, Any]:
        """A JSON-safe copy of the payload a verb's dry-run should mutate: the move's own
        overlay if an earlier step already touched this document, else the document as it
        is now."""
        return json.loads(
            json.dumps(
                overlay.get(export_id) or self.kernel.store.payload_of(export_id)
            )
        )

    def save(
        self,
        export_id: str,
        model: str,
        p: dict[str, Any],
        overlay: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """sldb's roundtrip of the mutated payload, then left in `overlay` so the next write
        of the move sees it."""
        self.kernel.roundtrip(model, p, store_of(export_id))
        overlay[export_id] = p
        return p
