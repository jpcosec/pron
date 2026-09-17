"""The kind of a field as the projection's schema declares it (spec 02): what decides whether
a proper name or an unmatched text is compared as a string. A field the schema does not list
counts as a string.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pron.world.lexicon import Lexicon


def field_kind(lex: Lexicon, model: str, fld: str) -> str:
    for f in lex.world.schema(model, lex.stores):
        if f["name"] == fld:
            return f["kind"]
    return "string"
