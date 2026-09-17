"""The `create` verb (spec 11 §7): a new document named by the projection's naming rule (or
by the sentence), its payload coerced and round-tripped, written in the projection's first
store. It stays outside `VERBS`: there is no export id before it runs, and `Kernel.undo`
inverts it together with `assert`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.actions.write import Write
from pron.kernel.display import render_name
from pron.kernel.ids import join_id
from pron.world.store_error import StoreError

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.kernel.kernel import Kernel


class CreateVerb:
    name = "create"

    def dry(
        self,
        kernel: "Kernel",
        model: str,
        payload: dict[str, Any],
        overlay: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """The payload a create would leave, coerced and round-tripped, registered in the overlay
        as `Model:$created` so later steps of the move can be checked against it."""
        missing = kernel.required_missing(model, payload)
        if missing:
            raise StoreError(f"{model} needs {', '.join(missing)}")
        full = kernel.fields.coerced(model, payload)
        kernel.roundtrip(model, full, kernel.write_store)
        overlay[join_id(kernel.write_store, model, "$created")] = full
        return full

    def execute(
        self,
        kernel: "Kernel",
        model: str,
        payload: dict[str, Any],
        related: dict[str, dict[str, Any]] | None = None,
        name: str | None = None,
    ) -> Write:
        name = self._name(kernel, model, payload, related, name)
        full = kernel.fields.coerced(model, payload)
        kernel.roundtrip(model, full, kernel.write_store)
        path = (
            kernel.store.root_of(kernel.write_store)
            / f"{model.lower()}s"
            / f"{name}.md"
        )
        export_id = kernel.store.create(model, name, full, path, kernel.write_store)
        w = Write("create", export_id, after=full, done=True, extra={"path": str(path)})
        kernel._after_write(export_id, w)
        return w

    @staticmethod
    def _name(
        kernel: "Kernel",
        model: str,
        payload: dict[str, Any],
        related: dict[str, dict[str, Any]] | None,
        name: str | None,
    ) -> str:
        """The name said, else the one the projection's naming rule renders."""
        if name is not None:
            return name
        rule = (kernel.projection.get("naming") or {}).get(model)
        if not rule:
            raise StoreError(f"no naming rule for {model}; say the name")
        return render_name(rule, payload, related or {})
