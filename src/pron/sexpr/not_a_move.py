"""A bare noun where a move is expected (spec 13): the noun is fine, the move is (show …)."""

from __future__ import annotations

from pron.sexpr.form_error import FormError


class NotAMove(FormError):
    """A bare noun where a move is expected (spec 13): the noun is fine, the move is (show …)."""
