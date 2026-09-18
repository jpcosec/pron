"""The `remove` verb (spec 11 §7): drop one value from a list field, or the field itself
when no value is named, and put back what was there to undo.
"""

from __future__ import annotations

from sldb.api import deep_delete

from pron.kernel.ids import model_of
from pron.kernel.actions.write import Write
from pron.world.doc_id import DocId


class RemoveVerb:
    name = "remove"

    def dry(self, kernel, export_id, field_name, value, overlay):
        model = model_of(export_id)
        p = kernel.dry.load(export_id, overlay)
        head = field_name.split(".")[0] if field_name else None
        if value is not None:
            lst = p.get(head)
            if isinstance(lst, list) and value in lst:
                lst.remove(value)
        elif head in p:
            deep_delete(p, field_name)
        return kernel.dry.save(export_id, model, p, overlay)

    def execute(self, kernel, export_id, field_name, value):
        assert field_name is not None
        kernel._guard(export_id)
        if value is None:
            w = self._field(kernel, export_id, field_name)
        else:
            w = self._value(kernel, export_id, field_name, value)
        if w.done:
            kernel._after_write(export_id, w)
        return w

    @staticmethod
    def _value(kernel, export_id, field_name, value):
        """One value out of a list field; not done when it is not there."""
        lst = kernel.store.payload(DocId.parse(export_id)).get(field_name)
        if not isinstance(lst, list) or value not in lst:
            return Write("remove", export_id, field_name, done=False, note="not there")
        before = list(lst)
        lst.remove(value)
        kernel.store.update_field(DocId.parse(export_id), field_name, lst)
        return Write("remove", export_id, field_name, before, lst, done=True)

    @staticmethod
    def _field(kernel, export_id, field_name):
        before = kernel.store.remove_field(DocId.parse(export_id), field_name)
        return Write("remove", export_id, field_name, before, None, done=True)

    def undo(self, kernel, write):
        if write.get("before") is None:
            return None
        doc_id, before = DocId.parse(write["address"]), write["before"]
        create = not isinstance(before, list)  # a scalar's field was deleted whole
        kernel.store.update_field(doc_id, write["field"], before, create=create)
        return Write(
            "undo", write["address"], write["field"], None, write["before"], done=True
        )
