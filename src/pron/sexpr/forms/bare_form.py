"""`(undo)` and `(refresh)` (spec 11, 13): a kernel verb with nothing to say but its name."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pron.kernel.parts.part import Part

if TYPE_CHECKING:
    from pron.sexpr.forms.compiler import Compiler


class BareForm:
    def __init__(self, head: str):
        self.head = head

    def __call__(self, compiler: Compiler) -> Part:
        return Part(self.head, verb=compiler.words.kernel(self.head))
