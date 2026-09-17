"""One write of a move (spec 11 §7): the verb, the address it touched, the field, the value
before and after, whether it was actually done, and whatever extra the verb recorded for the
undo. `record()` is what the MoveDoc keeps.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pron.kernel.kernel import Kernel


@dataclass
class Write:
    verb: str
    address: str  # Model:doc export id
    field_name: str | None = None
    before: Any = None
    after: Any = None
    done: bool = False
    note: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def record(self) -> dict[str, Any]:
        return {
            "verb": self.verb,
            "address": self.address,
            "field": self.field_name,
            "before": self.before,
            "after": self.after,
            "done": self.done,
            "note": self.note,
            **self.extra,
        }


def restore_field(kernel: "Kernel", write: dict[str, Any]) -> Write:
    """Undo for a verb whose inverse is simply setting the field back to what it was
    (`change`, `clean`): both leave the field as one value and are undone the same way."""
    before = kernel.store.update_field_of(
        write["address"], write["field"], write["before"]
    )
    return Write("undo", write["address"], write["field"], before, write["before"], done=True)
