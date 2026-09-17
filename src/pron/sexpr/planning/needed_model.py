"""The class a role of a part has to be (spec 02, 05, 13).

A relation says it: the first of the source types for the subject, of the target types for
the object. An action's model says it; a field that several classes have says only which
classes can be meant. Planning resolves each phrase against this class, and
the forms a sentence said name it, so both ask here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pron.kernel.parts.part import Part

if TYPE_CHECKING:
    from pron.world.lexicon import Lexicon


def needed_model(part: Part, role: str, lex: Lexicon) -> str | None:
    """What class this role has to be: a relation says it, an action's model says it."""
    if part.kind in ("read", "assert") and part.verb is not None and part.verb.relation:
        return _relation_model(part.verb.relation, role, lex)
    if part.kind == "action" and "model" in part.payload:
        return part.payload["model"]  # None: a field of several classes names none
    if part.kind == "action":
        return part.verb.model if part.verb else None
    return None


def field_classes(part: Part, lex: Lexicon) -> list[str] | None:
    """The classes that have the field an action writes, when no single class was said: any
    of them can be the referent's antecedent (spec 06)."""
    if part.kind != "action" or part.field_name is None:
        return None
    return [
        m
        for m in lex.models
        if any(w.field_name == part.field_name for w in lex.fields_of(m))
    ]


def _relation_model(relation: str, role: str, lex: Lexicon) -> str | None:
    rt = lex.relation_types.get(relation, {})
    types = rt.get("source_types" if role == "subject" else "target_types") or []
    return types[0] if types else None
