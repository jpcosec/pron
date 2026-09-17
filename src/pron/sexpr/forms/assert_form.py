"""`(assert relation SUBJECT OBJECT)` (spec 03, 13): an edge to write between two nouns."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.parts.part import Part

if TYPE_CHECKING:
    from pron.sexpr.forms.compiler import Compiler


class AssertForm:
    head = "assert"

    def __call__(self, compiler: Compiler, relation: Any, subject: Any, obj: Any) -> Part:
        w = compiler.words.relation(str(relation))
        return Part(
            "assert", subject=compiler.noun(subject), object=compiler.noun(obj), verb=w
        )
