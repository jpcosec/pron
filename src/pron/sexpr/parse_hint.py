"""What to say when nothing calzó (spec 05 §Calce aproximado P4, spec 13).

Real sentences of *this* world when its lexicon has any, never another world's fixture
sentences; only a world with no examples of its own falls back to the names of the
constructions the surface knows.
"""

from __future__ import annotations

from pron.surface.interpret import construction_names
from pron.world.lexicon import Lexicon


def cannot_parse_hint(lex: Lexicon) -> str:
    """Sentences this world's lexicon can show, or the constructions the surface knows."""
    real = lex.examples()
    if real:
        return "I can understand: " + " · ".join(real) + " …"
    return "I can understand constructions like: " + ", ".join(construction_names())
