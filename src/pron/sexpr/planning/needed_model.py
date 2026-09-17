"""The class a role of a part has to be (spec 02, 05, 13).

A relation says it: the first of the source types for the subject, of the target types for
the object. An action's model says it. Planning resolves each phrase against this class, and
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
    if part.kind == "action":
        return part.payload.get("model") or (part.verb.model if part.verb else None)
    return None


def _relation_model(relation: str, role: str, lex: Lexicon) -> str | None:
    rt = lex.relation_types.get(relation, {})
    types = rt.get("source_types" if role == "subject" else "target_types") or []
    return types[0] if types else None
