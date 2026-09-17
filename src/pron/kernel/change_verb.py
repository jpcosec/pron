"""The `change` verb (spec 11 §7): set one field, with its coercion and its state machine
transition checked the same way in the dry run and in the real write.
"""

from __future__ import annotations

from sldb.cli.dict_utils import deep_set

from pron.kernel.ids import model_of
from pron.kernel.write import restore_field
from pron.world.store_error import StoreError


class ChangeVerb:
    name = "change"

    def dry(self, kernel, export_id, field_name, value, overlay):
        model = model_of(export_id)
        p = kernel._dry_load(export_id, overlay)
        if field_name is None:
            raise StoreError("change requires a field")
        head = field_name.split(".")[0]
        value = kernel.coerce(model, field_name, value)
        legal, why, queries = kernel.verbs.transition(
            model, field_name, export_id, p.get(head), value, overlay=overlay
        )
        kernel.notes += queries
        if queries or "legal" in why:
            kernel.notes.append(why)
        if not legal:
            raise StoreError(why)
        deep_set(p, field_name, value, create=True)
        return kernel._dry_save(export_id, model, p, overlay)

    def execute(self, kernel, export_id, field_name, value):
        assert field_name is not None
        return kernel.change(export_id, field_name, value)

    def undo(self, kernel, write):
        return restore_field(kernel, write)
