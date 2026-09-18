"""Arguments a write tool cannot compile to a form (spec 14 §4): refused before anything is
evaluated, so no move is made."""

from __future__ import annotations


class ArgError(ValueError):
    """A tool's JSON arguments do not make a form."""
