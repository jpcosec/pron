"""`(why [NOUN])` (spec 07, 13): the moves that left a document as it is. A noun that gives
its document names the target; any other leaves it to the dialogue.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.parts.part import Part
from pron.sexpr.resolving.resolution import address_to_export_id

if TYPE_CHECKING:
    from pron.sexpr.forms.compiler import Compiler


class WhyForm:
    head = "why"

    def __call__(self, compiler: Compiler, noun: Any = None) -> Part:
        part = Part("why")
        if noun is not None:
            np = compiler.noun(noun)
            if np.given:
                part.payload["target"] = address_to_export_id(np.given[0])
        return part
