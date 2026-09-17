"""Undoing the last move that wrote (spec 07, 11 §7).

The ledger says which move it was — this speaker's, if there is one — and the kernel
inverts each of its writes, refusing any document that has changed since. Nothing is
forced: a write that cannot be taken back is reported, not retried.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.actions.write import Write
from pron.world.store_error import StoreError

if TYPE_CHECKING:
    from pron.kernel.kernel import Kernel
    from pron.sexpr.dialogue.dialogue import Dialogue
    from pron.sexpr.turn.ledger import Ledger
    from pron.sexpr.turn.move_context import MoveContext


class UndoExecutor:
    """The last move with writes, inverted."""

    def __init__(self, kernel: Kernel, ledger: Ledger, dialogue: Dialogue):
        self.kernel, self.ledger, self.dialogue = kernel, ledger, dialogue

    def __call__(self, ctx: MoveContext) -> str:
        if not self.kernel.allowed("undo"):
            raise StoreError("in this session I cannot undo")
        move = self.ledger.last_with_write(self.dialogue.speaker or None)
        if move is None:
            return "Nothing to undo."
        writes = self.kernel.undo(move)
        self._note(writes, ctx)
        ctx.record["undoes"] = move["id"]
        return _text(move, writes)

    @staticmethod
    def _note(writes: list[Write], ctx: MoveContext) -> None:
        for w in writes:
            ctx.trace.append(_line(w))
            ctx.record["writes"].append(w.record())


def _line(w: Write) -> str:
    return (
        f"undo {w.address}"
        + (f".{w.field_name}" if w.field_name else "")
        + f": {w.before!r} → {w.after!r}"
        + ("" if w.done else f" ({w.note})")
    )


def _text(move: dict[str, Any], writes: list[Write]) -> str:
    skipped = [w.note for w in writes if not w.done]
    return (
        f"Undid {move['id']} ({len([w for w in writes if w.done])} write(s))."
        + (" Not touched: " + "; ".join(skipped) + "." if skipped else "")
    )
