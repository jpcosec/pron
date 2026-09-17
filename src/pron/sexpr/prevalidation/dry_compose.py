"""Simulating a composition (spec 11 §7, spec 05): every step, in order, over the overlay.

The steps of a composition run one after another and the later ones may name what the
earlier ones made, as `$created`. That is what makes the simulation worth doing here: a
step that names `$created` before any step created anything is a malformed declaration,
and it is caught before the first real write — and before anything is even asked of the
store. A `change` against `$created` is skipped: the document does not exist yet, so there
is no payload to check the transition against.
"""

from __future__ import annotations

from typing import Any

from pron.kernel.ids import join_id
from pron.kernel.parts.part import Part
from pron.sexpr.turn.collaborator import Collaborator
from pron.sexpr.prevalidation.dry_assert import DryAssert
from pron.world.store_error import StoreError


class DryCompose(Collaborator):
    """A composition's steps, simulated in the order they will run."""

    def __call__(
        self,
        part: Part,
        plan: dict[str, Any],
        overlay: dict[str, dict[str, Any]],
    ) -> None:
        assert part.verb is not None
        self.overlay = overlay
        self.created_model: str | None = None
        self.literals = {
            k: v for k, v in part.payload.items() if not k.startswith("_")
        }
        steps = part.verb.payload.get("steps", [])
        for step, resolved in zip(steps, plan["steps"]):
            self._step(step, resolved)

    def _step(self, step: dict[str, Any], resolved: dict[str, Any]) -> None:
        if (
            "$created" in (step.get("source"), step.get("target"))
            and self.created_model is None
        ):
            raise StoreError("composition references $created before create")
        fn = getattr(self, "_do_" + str(step.get("do")), None)
        if fn is not None:
            fn(step, resolved, self._created_id())

    def _created_id(self) -> str | None:
        if self.created_model is None:
            return None
        return join_id(self.s.write_store, self.created_model, "$created")

    def _do_create(self, step, resolved, created_id: str | None) -> None:
        self.created_model = step["model"]
        if self.created_model is None:
            raise StoreError("create requires a model")
        self.s.kernel.dry_create(self.created_model, self._fields(), self.overlay)

    def _fields(self) -> dict[str, Any]:
        """The literals of the sentence this model has a field for."""
        names = {f["name"] for f in self.s.kernel.schema(self.created_model)}
        return {k: v for k, v in self.literals.items() if k in names}

    def _do_assert(self, step, resolved, created_id: str | None) -> None:
        src = _ids(step, resolved, "source", created_id)
        tgt = _ids(step, resolved, "target", created_id)
        DryAssert(self.s)(step["relation"], src, tgt, self.overlay)

    def _do_change(self, step, resolved, created_id: str | None) -> None:
        on_created = step.get("target") == "$created"
        tgt = created_id if on_created else resolved["target"].export_ids()[0]
        if tgt is None:
            raise StoreError("composition references $created before create")
        if not tgt.endswith(":$created"):
            self.s.kernel.dry_run(
                "change", tgt, step["field"], step["value"], self.overlay
            )


def _ids(
    step: dict[str, Any], resolved: dict[str, Any], key: str, created_id: str | None
) -> list[str]:
    """One side of an assert step: what the composition made, or what the slot resolved."""
    if step.get(key) == "$created":
        return [created_id] if created_id is not None else []
    return resolved[key].export_ids()
