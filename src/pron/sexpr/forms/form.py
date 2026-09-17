"""What a move form is (spec 13): one object per head that turns the form's arguments into
the part a session plans and runs, so what each form means lives in one place — the way a
kernel verb knows its own dry run, execution and undo (spec 11 §7). It is called with the
compiler, through which it compiles its nouns and checks its words, and the form's
arguments; how many it takes is its own signature.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from pron.kernel.parts.part import Part


class Form(Protocol):
    head: str

    def __call__(self, *args: Any, **kwargs: Any) -> Part:
        """The part `(head args…)` says, given the compiler first; FormError when it is not
        well made."""
        ...
