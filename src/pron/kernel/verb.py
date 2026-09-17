"""What a plain action verb is (spec 11 §7): one object that knows its own dry-run
simulation, real execution, and undo. Before this, each verb's behavior was reimplemented
independently in `Kernel.dry_run`, `Kernel.undo`, `Session._dry_parts` and
`Session._action`; a Verb is the one place a verb's semantics live, so a new or changed
verb touches one class instead of four call sites. `create` and `assert` stay outside this
protocol: their shapes (no export_id yet; a RelationDoc write) don't fit the same
signature, and `Kernel.undo` already inverts them together.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

from pron.kernel.write import Write

if TYPE_CHECKING:
    from pron.kernel.kernel import Kernel


class Verb(Protocol):
    name: str

    def dry(
        self,
        kernel: "Kernel",
        export_id: str,
        field_name: str | None,
        value: Any,
        overlay: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """What this write would leave in `export_id`'s payload, without writing (spec 11 §7)."""
        ...

    def execute(
        self, kernel: "Kernel", export_id: str, field_name: str | None, value: Any
    ) -> Write:
        """The real write against `kernel.store`."""
        ...

    def undo(self, kernel: "Kernel", write: dict[str, Any]) -> Write | None:
        """The inverse of a recorded write, or None if there is nothing to invert."""
        ...
