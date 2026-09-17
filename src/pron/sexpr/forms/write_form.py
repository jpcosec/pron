"""The kernel's plain writes as forms (spec 04, 11 §7, 13): `(change NOUN field value)`,
`(add NOUN field value)`, `(remove NOUN field [value])`, `(clean NOUN field)` and
`(forget NOUN)`. One class, one instance per verb: they differ only in how many arguments
each takes.
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
        return Part(
            "action",
            subject=compiler.noun(noun),
            verb=compiler.words.kernel(self.head),
            field_name=str(field_name) if field_name is not None else None,
            value=unvalue(value),
            payload={"verb": self.head},
        )
