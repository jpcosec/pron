"""The `remove` verb (spec 11 §7): drop one value from a list field, or the field itself
when no value is named, and put back what was there to undo.
"""

from __future__ import annotations

from sldb.cli.dict_utils import deep_delete

from pron.kernel.ids import model_of
from pron.kernel.write import Write


class RemoveVerb:
    name = "remove"

    def dry(self, kernel, export_id, field_name, value, overlay):
        model = model_of(export_id)
        p = kernel._dry_load(export_id, overlay)
        head = field_name.split(".")[0] if field_name else None
        if value is not None:
            lst = p.get(head)
            if isinstance(lst, list) and value in lst:
                lst.remove(value)
        elif head in p:
            deep_delete(p, field_name)
        return kernel._dry_save(export_id, model, p, overlay)

    def execute(self, kernel, export_id, field_name, value):
        assert field_name is not None
        return kernel.remove(export_id, field_name, value)

    def undo(self, kernel, write):
        if write.get("before") is None:
            return None
        if isinstance(write["before"], list):
            kernel.store.update_field_of(
                write["address"], write["field"], write["before"]
            )
        else:
            kernel.store.update_field_of(
                write["address"], write["field"], write["before"], create=True
            )
        return Write(
            "undo", write["address"], write["field"], None, write["before"], done=True
        )
