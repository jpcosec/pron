"""What a badly made form raises (spec 13). The two cases a caller distinguishes —
a bare noun where a move belongs, an unknown word — are subclasses of this one.
"""

from __future__ import annotations


class FormError(ValueError):
    """A form that is not well made."""
