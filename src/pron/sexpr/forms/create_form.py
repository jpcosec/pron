"""`(create Model [(as "doc-name")] (field value) ...)` (spec 04, 13): a new document of a
model of the projection, with the fields it is born with and, if given, its name.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.parts.noun_phrase import NounPhrase
from pron.kernel.parts.part import Part
from pron.kernel.sexp.read_write import write
from pron.sexpr.forms.form_error import FormError
from pron.sexpr.forms.syntax import is_clause, unvalue

if TYPE_CHECKING:
    from pron.sexpr.forms.compiler import Compiler


class CreateForm:
    head = "create"

    def __call__(self, compiler: Compiler, model: Any, *fields: Any) -> Part:
        m = str(model)
        compiler.words.need_model(m)
        name = next((str(f[1]) for f in fields if is_clause(f, "as")), None)
        payload = _field_pairs(tuple(f for f in fields if not is_clause(f, "as")))
        extra = {"name": name} if name else {}
        return Part(
            "action",
            subject=NounPhrase(m, "any", "singular"),
            verb=compiler.words.kernel("create"),
            payload={"verb": "create", "fields": payload, **extra},
        )


def _field_pairs(fields: tuple[Any, ...]) -> dict[str, Any]:
    out = {}
    for pair in fields:
        if not isinstance(pair, list) or len(pair) != 2:
            raise FormError(f"a field is (name value), got {write(pair)}")
        out[str(pair[0])] = unvalue(pair[1])
    return out
