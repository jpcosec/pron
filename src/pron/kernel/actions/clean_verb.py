"""The `clean` verb (spec 11 §7): drop the empty and repeated items of a list field, and
restore the list as it was to undo.
"""

from __future__ import annotations

from pron.kernel.ids import model_of
from pron.kernel.actions.write import Write, restore_field
from pron.world.doc_id import DocId
from pron.world.storage.cleaned_list import without_empty_or_repeated


class CleanVerb:
    name = "clean"

    def dry(self, kernel, export_id, field_name, value, overlay):
        model = model_of(export_id)
        p = kernel.dry.load(export_id, overlay)
        head = field_name.split(".")[0] if field_name else None
        lst = p.get(head)
        if isinstance(lst, list):
            p[head] = without_empty_or_repeated(lst)
        return kernel.dry.save(export_id, model, p, overlay)

    def execute(self, kernel, export_id, field_name, value):
        assert field_name is not None
        kernel._guard(export_id)
        before = kernel.store.clean(DocId.parse_plain(export_id), field_name)
        w = Write(
            "clean",
            export_id,
            field_name,
            before,
            kernel.store.payload(DocId.parse_plain(export_id)).get(field_name),
            done=True,
        )
        kernel._after_write(export_id, w)
        return w

    def undo(self, kernel, write):
        return restore_field(kernel, write)
