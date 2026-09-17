"""The symbol atom of pron's structured language (spec 06, 13): a form name, a relation,
a model, a field. Every other atom is a string, an integer, a float, or true/false/nil.
"""

from __future__ import annotations


class Sym(str):
    """A bare symbol: a form name, a relation, a model, a field."""

    def __repr__(self) -> str:
        return f"Sym({str.__repr__(self)})"
