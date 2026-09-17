"""Doing an action part (spec 11 §7): a create, or the same verb over every target.

A create makes one document and answers with its natural name. Every other verb runs over
each document the subject resolved to: the whole batch is guarded and coerced before the
first of them is written, then each write is the verb's own `Verb.execute`
(kernel/actions/verb_registry.py) — the one place that verb's semantics live — traced with what it
changed, and recorded for undo. A write that had nothing to do is not a failure: the answer
says how many were already like that.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.ids import address_of, model_of
from pron.kernel.parts.part import Part
from pron.kernel.actions.verb_registry import VERBS
from pron.kernel.actions.write import Write
from pron.sexpr.prevalidation.action_verb import action_verb
from pron.world.store_error import StoreError

if TYPE_CHECKING:
    from pron.kernel.display import Display
    from pron.kernel.kernel import Kernel
    from pron.sexpr.dialogue.dialogue import Dialogue
    from pron.sexpr.turn.move_context import MoveContext


class ActionExecutor:
    """One action part, written; and whether it wrote anything."""

    def __init__(self, kernel: Kernel, dialogue: Dialogue, display: Display):
        self.kernel, self.dialogue, self.display = kernel, dialogue, display

    def __call__(
        self, part: Part, plan: dict[str, Any], ctx: MoveContext
    ) -> tuple[str, bool]:
        verb = action_verb(part)
        if not self.kernel.allowed(verb):
            raise StoreError(f"in this session I cannot {verb}")
        if verb == "create":
            return self._create(part, ctx), True
        return self._batch(verb, part, plan, ctx)

    # -- create --------------------------------------------------------------------------

    def _create(self, part: Part, ctx: MoveContext) -> str:
        assert part.subject is not None and part.subject.model is not None
        model, fields = part.subject.model, part.payload["fields"]
        w = self.kernel.create(model, fields, name=part.payload.get("name"))
        ctx.trace.append(f"docs create --model {model} {w.address} {w.after}")
        ctx.record["writes"].append(w.record())
        addr = address_of(w.address)
        self.dialogue.remember([addr], model)
        self.dialogue.last_written = w.address
        return f"Created {model.lower()} {self.display.name(addr)}."

    # -- the same verb over every target -------------------------------------------------

    def _batch(
        self, verb: str | None, part: Part, plan: dict[str, Any], ctx: MoveContext
    ) -> tuple[str, bool]:
        targets = plan["subject"].export_ids()
        self._precheck(verb, part, targets)
        writes = [self._one(verb, part, e, ctx) for e in targets]
        self.dialogue.remember(
            plan["subject"].addresses, plan["subject"].phrase.model
        )
        self.dialogue.last_written = targets[0] if targets else None
        done = [w for w in writes if w.done]
        skipped = [w for w in writes if not w.done]
        return _text(verb, targets, done, skipped), bool(done)

    def _precheck(self, verb: str | None, part: Part, targets: list[str]) -> None:
        """The whole batch guarded and coerced before the first write (spec 11 §7)."""
        for e in targets:
            self.kernel.expect(e)
        for e in targets:
            if verb == "change":
                if part.field_name is None:
                    raise StoreError("change requires a field")
                self.kernel.coerce(model_of(e), part.field_name, part.value)

    def _one(self, verb: str | None, part: Part, e: str, ctx: MoveContext) -> Write:
        if verb in ("change", "add", "remove", "clean") and part.field_name is None:
            raise StoreError(f"{verb} requires a field")
        action = VERBS.get(verb)
        if action is None:
            raise StoreError(f"unknown verb {verb}")
        w = action.execute(self.kernel, e, part.field_name, part.value)
        self._notes(ctx)
        ctx.trace.append(_line(w))
        ctx.record["writes"].append(w.record())
        return w

    def _notes(self, ctx: MoveContext) -> None:
        ctx.trace.extend(self.kernel.notes)
        ctx.record["queries"].extend(self.kernel.notes)
        self.kernel.notes = []


def _line(w: Write) -> str:
    return (
        f"{w.verb} {w.address}"
        + (f".{w.field_name}: {w.before!r} → {w.after!r}" if w.field_name else "")
        + ("" if w.done else f" (not done: {w.note})")
    )


def _text(
    verb: str | None, targets: list[str], done: list[Write], skipped: list[Write]
) -> str:
    if verb == "forget":
        return f"Forgot {len(done)}."
    if len(targets) == 1:
        return "Done." if done else f"Nothing to do ({skipped[0].note})."
    return (
        f"Done on {len(done)}"
        + (f"; {len(skipped)} already like that" if skipped else "")
        + "."
    )
