"""The `add` verb (spec 11 §7): append a value to a list field, once, and remove it again
to undo.
"""

from __future__ import annotations

from sldb.cli.dict_utils import deep_get

from pron.kernel.ids import model_of
from pron.kernel.actions.write import Write
from pron.world.store_error import StoreError


class AddVerb:
    name = "add"

    def dry(self, kernel, export_id, field_name, value, overlay):
        model = model_of(export_id)
        p = kernel.dry.load(export_id, overlay)
        head = field_name.split(".")[0] if field_name else None
        lst = deep_get(p, field_name) if head in p else None
        if not isinstance(lst, list):
            raise StoreError(f"{field_name} is not a list field")
        if value not in lst:
            lst.append(value)
        return kernel.dry.save(export_id, model, p, overlay)

    def execute(self, kernel, export_id, field_name, value):
        assert field_name is not None
        kernel._guard(export_id)
        lst = kernel.store.payload_of(export_id).get(field_name)
        if isinstance(lst, list) and value in lst:
            return Write(
                "add", export_id, field_name, lst, lst, done=False, note="already there"
            )
        idx = kernel.store.append_of(export_id, field_name, value)
        w = Write(
            "add", export_id, field_name, None, value, done=True, extra={"index": idx}
        )
        kernel._after_write(export_id, w)
        return w

    def undo(self, kernel, write):
        lst = kernel.store.payload_of(write["address"]).get(write["field"], [])
        if write["after"] in lst:
            lst.remove(write["after"])
            kernel.store.update_field_of(write["address"], write["field"], lst)
        return Write(
            "undo", write["address"], write["field"], write["after"], None, done=True
        )
