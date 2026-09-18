"""The kernel's plain writes as forms (spec 04, 11 §7, 13): `(change NOUN field value)`,
`(add NOUN field value)`, `(remove NOUN field [value])`, `(clean NOUN field)` and
`(forget NOUN)`. One class, one instance per verb: they differ only in how many arguments
each takes. The noun of a forget may be an edge's RelationDoc: forgetting it negates the edge
(spec 14 §4).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.parts.part import Part
from pron.sexpr.forms.syntax import unvalue

if TYPE_CHECKING:
    from pron.sexpr.forms.compiler import Compiler


class WriteForm:
    def __init__(self, head: str, required: int, optional: int = 0):
        self.head, self.required, self.optional = head, required, optional

    def __call__(self, compiler: Compiler, *args: Any) -> Part:
        if not self.required <= len(args) <= self.required + self.optional:
            raise TypeError(
                f"({self.head} …) takes {self.required} to "
                f"{self.required + self.optional} arguments, got {len(args)}"
            )
        noun, field_name, value = (*args, None, None)[:3]
        subject = compiler.noun.negated if self.head == "forget" else compiler.noun
        return Part(
            "action",
            subject=subject(noun),
            verb=compiler.words.kernel(self.head),
            field_name=str(field_name) if field_name is not None else None,
            value=unvalue(value),
            payload={"verb": self.head},
        )
