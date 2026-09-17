"""What the door to sldb raises (spec 02, 04): sldb refused or could not do what was asked.
Every read or write by address goes through it, so a caller never sees an sldb exception.
"""

from __future__ import annotations


class StoreError(RuntimeError):
    """sldb refused or could not do what was asked."""
