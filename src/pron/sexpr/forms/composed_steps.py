"""The steps of a composed sentence, read from its forms (spec 05, 13): `(create M)` makes the
document, `(assert R SOURCE TARGET)` writes an edge, `(change NOUN field value)` a field. A
noun in a step is a slot the sentence fills: `(created)` is what the create left, `(it …)` the
referent of the sentence, `(a M)` its phrase of class M.
"""

from __future__ import annotations

from typing import Any

from pron.sexpr.forms.syntax import form_head


def step_of(form: Any) -> dict[str, Any]:
    head = form_head(form, ValueError)
    if head == "create":
        return {"do": "create", "model": str(form[1]), "fields": "$literals"}
    if head == "assert":
        return {
            "do": "assert",
            "relation": str(form[1]),
            "source": slot_of(form[2]),
            "target": slot_of(form[3]),
        }
    if head == "change":
        return {
            "do": "change",
            "target": slot_of(form[1]),
            "field": str(form[2]),
            "value": form[3],
        }
    raise ValueError(
        f"a composed sentence takes create, assert and change, not ({head} …)"
    )


def slot_of(noun: Any) -> str:
    head = form_head(noun, ValueError)
    if head == "created":
        return "$created"
    if head in ("it", "them"):
        return f"$referent:{noun[2]}" if len(noun) > 2 else "$referent:"
    if head in ("a", "the", "all"):
        return f"$object:{noun[1]}"
    raise ValueError(
        f"a slot of a composed sentence is (created), (it …) or (a M), not ({head} …)"
    )
