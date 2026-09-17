"""The `change` verb (spec 11 §7): set one field, with its coercion and its state machine
transition checked the same way in the dry run and in the real write.
"""

from __future__ import annotations

from sldb.api import deep_set

from pron.kernel.ids import model_of
from pron.kernel.actions.write import Write, restore_field
from pron.world.store_error import StoreError


class ChangeVerb:
    name = "change"

    def dry(self, kernel, export_id, field_name, value, overlay):
        model = model_of(export_id)
        p = kernel.dry.load(export_id, overlay)
        if field_name is None:
            raise StoreError("change requires a field")
        value = kernel.coerce(model, field_name, value)
        before = p.get(field_name.split(".")[0])
        self._transition(kernel, model, field_name, export_id, before, value, overlay)
        deep_set(p, field_name, value, create=True)
        return kernel.dry.save(export_id, model, p, overlay)

    def execute(self, kernel, export_id, field_name, value):
        assert field_name is not None
        model = model_of(export_id)
        value = kernel.coerce(model, field_name, value)
        before = kernel.store.payload_of(export_id).get(field_name.split(".")[0])
        self._transition(kernel, model, field_name, export_id, before, value)
        kernel._guard(export_id)
        before = kernel.store.update_field_of(export_id, field_name, value)
        w = Write("change", export_id, field_name, before, value, done=True)
        kernel._after_write(export_id, w)
        return w

    @staticmethod
    def _transition(
        kernel,
        model,
        field_name,
        export_id,
        before,
        value,
        overlay=None,
    ):
        """The state machine's word on a change (spec 10 §3), noted for the trace; an illegal
        transition is refused."""
        legal, why, queries = kernel.verbs.transition(
            model, field_name, export_id, before, value, overlay=overlay
        )
        kernel.notes += queries
        if queries or "legal" in why:
            kernel.notes.append(why)
        if not legal:
            raise StoreError(why)

    def undo(self, kernel, write):
        return restore_field(kernel, write)
