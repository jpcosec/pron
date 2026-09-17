"""The `clean` verb (spec 11 §7): drop the empty and repeated items of a list field, and
restore the list as it was to undo.
"""

from __future__ import annotations

import json
from typing import Any

from pron.kernel.ids import model_of
from pron.kernel.write import restore_field


class CleanVerb:
    name = "clean"

    def dry(self, kernel, export_id, field_name, value, overlay):
        model = model_of(export_id)
        p = kernel._dry_load(export_id, overlay)
        head = field_name.split(".")[0] if field_name else None
        lst = p.get(head)
        if isinstance(lst, list):
            seen: set[str] = set()
            out: list[Any] = []
            for item in lst:
                k = json.dumps(item, sort_keys=True)
                if item in (None, "", [], {}) or k in seen:
                    continue
                seen.add(k)
                out.append(item)
            p[head] = out
        return kernel._dry_save(export_id, model, p, overlay)

    def execute(self, kernel, export_id, field_name, value):
        assert field_name is not None
        return kernel.clean(export_id, field_name)

    def undo(self, kernel, write):
        return restore_field(kernel, write)
