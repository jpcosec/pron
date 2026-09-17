"""`(show NOUN)` (spec 13): the documents a noun names, as a nominal part."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.parts.part import Part

if TYPE_CHECKING:
    from pron.sexpr.forms.compiler import Compiler


class ShowForm:
    head = "show"

    def __call__(self, compiler: Compiler, noun: Any) -> Part:
        return Part("nominal", subject=compiler.noun(noun))
