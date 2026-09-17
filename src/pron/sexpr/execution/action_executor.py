"""Doing an action part (spec 11 §7): a create, or the same verb over every target.

A create makes one document and answers with its natural name. Every other verb runs over
each document the subject resolved to: the whole batch is guarded and coerced before the
first of them is written, then each write is the verb's own `Verb.execute`
(kernel/actions/verb_registry.py) — the one place that verb's semantics live — traced with what it
changed, and recorded for undo. A write that had nothing to do is not a failure: the answer
says how many were already like that.
"""

from __future__ import annotations

from typing import Any

from pron.kernel.ids import address_of, model_of
from pron.kernel.parts.part import Part
from pron.kernel.actions.verb_registry import VERBS
from pron.kernel.actions.write import Write
from pron.sexpr.prevalidation.action_verb import action_verb
from pron.sexpr.turn.collaborator import Collaborator
from pron.world.store_error import StoreError


class ActionExecutor(Collaborator):
    """One action part, written; and whether it wrote anything."""

    def __call__(
        self,
        part: Part,
        plan: dict[str, Any],
        trace: list[str],
        record: dict[str, Any],
    ) -> tuple[str, bool]:
        verb = action_verb(part)
        if not self.s.kernel.allowed(verb):
            raise StoreError(f"in this session I cannot {verb}")
        if verb == "create":
            return self._create(part, trace, record), True
        return self._batch(verb, part, plan, trace, record)

    # -- create --------------------------------------------------------------------------

    def _create(self, part: Part, trace: list[str], record: dict[str, Any]) -> str:
        assert part.subject is not None and part.subject.model is not None
        model, fields = part.subject.model, part.payload["fields"]
        w = self.s.kernel.create(model, fields, name=part.payload.get("name"))
        trace.append(f"docs create --model {model} {w.address} {w.after}")
        record["writes"].append(w.record())
        addr = address_of(w.address)
        self.s.dialogue.remember([addr], model)
        self.s.dialogue.last_written = w.address
        return f"Created {model.lower()} {self.s.display.name(addr)}."

    # -- the same verb over every target -------------------------------------------------

    def _batch(
        self,
        verb: str | None,
        part: Part,
        plan: dict[str, Any],
        trace: list[str],
        record: dict[str, Any],
    ) -> tuple[str, bool]:
        targets = plan["subject"].export_ids()
        self._precheck(verb, part, targets)
        writes = [self._one(verb, part, e, trace, record) for e in targets]
        self.s.dialogue.remember(
            plan["subject"].addresses, plan["subject"].phrase.model
        )
        self.s.dialogue.last_written = targets[0] if targets else None
        done = [w for w in writes if w.done]
        skipped = [w for w in writes if not w.done]
        return _text(verb, targets, done, skipped), bool(done)

    def _precheck(self, verb: str | None, part: Part, targets: list[str]) -> None:
        """The whole batch guarded and coerced before the first write (spec 11 §7)."""
        for e in targets:
            self.s.kernel.expect(e)
        for e in targets:
            if verb == "change":
                if part.field_name is None:
                    raise StoreError("change requires a field")
                self.s.kernel.coerce(model_of(e), part.field_name, part.value)

    def _one(
        self,
        verb: str | None,
        part: Part,
        e: str,
        trace: list[str],
        record: dict[str, Any],
    ) -> Write:
        if verb in ("change", "add", "remove", "clean") and part.field_name is None:
            raise StoreError(f"{verb} requires a field")
        action = VERBS.get(verb)
        if action is None:
            raise StoreError(f"unknown verb {verb}")
        w = action.execute(self.s.kernel, e, part.field_name, part.value)
        self._notes(trace, record)
        trace.append(_line(w))
        record["writes"].append(w.record())
        return w

    def _notes(self, trace: list[str], record: dict[str, Any]) -> None:
        trace.extend(self.s.kernel.notes)
        record["queries"].extend(self.s.kernel.notes)
        self.s.kernel.notes = []


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
