"""A model, relation or alias the session's projection does not have (spec 01, 13): the form
is well made, the word is simply not in this world.
"""

from __future__ import annotations

from pron.sexpr.forms.form_error import FormError


class UnknownWord(FormError):
    """A model, relation or alias the session's projection does not have (spec 01): missing."""
