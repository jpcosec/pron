"""Which plain action verb an action part does (spec 11 §7, spec 13).

A part may say the verb itself — `(change NOUN field value)` — or say an alias that stands
for one; the pre-validation and the execution of an action both ask the same question, and
they ask it here.
"""

from __future__ import annotations

from pron.kernel.parts.part import Part


def action_verb(part: Part) -> str | None:
    """The verb the form said, or the one the alias behind it stands for."""
    return part.payload.get(
        "verb", part.verb.payload.get("verb") if part.verb else None
    )
