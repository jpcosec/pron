"""`(targets relation [NOUN] [(of Model)] [(where "...")])` and its mirror `(sources …)`
(spec 03, 13): a read of a relation's edges. `targets` gives the subject and asks for what it
relates to; `sources` gives the object and asks for what relates to it. `(of M)` and
`(where …)` describe the side asked about.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.parts.noun_phrase import NounPhrase
from pron.kernel.parts.part import Part
from pron.sexpr.forms.form_error import FormError
from pron.sexpr.forms.syntax import NOUN_HEADS, form_head

if TYPE_CHECKING:
    from pron.sexpr.forms.compiler import Compiler


class ReadForm:
    def __init__(self, head: str, asked: str):
        self.head, self.asked = head, asked
        self.given_role = "subject" if asked == "object" else "object"

    def __call__(self, compiler: Compiler, relation: Any, *rest: Any) -> Part:
        w = compiler.words.relation(str(relation))
        part = Part("read", verb=w, payload={"asked": self.asked, "where": []})
        asked_model = None
        for item in rest:
            asked_model = self._clause(compiler, part, item, asked_model)
        if asked_model is not None or part.payload["where"]:
            where = list(part.payload["where"])
            setattr(
                part,
                self.asked,
                NounPhrase(asked_model, None, "plural", predicates=where),
            )
        return part

    def _clause(
        self, compiler: Compiler, part: Part, item: Any, asked_model: str | None
    ) -> str | None:
        """One argument of the read; the class asked about, as far as the arguments said it."""
        h = form_head(item)
        if h in NOUN_HEADS:
            setattr(part, self.given_role, compiler.noun(item))
        elif h == "of":
            return str(item[1])
        elif h == "where":
            part.payload["where"].append(str(item[1]))
        else:
            raise FormError(f"unknown clause in a read: ({h} …)")
        return asked_model
