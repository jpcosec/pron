"""Ranking candidates for a query (spec 11 §2), re-exported from sldb: `Matcher` and the
`cosine` similarity over two vectors.
"""

from __future__ import annotations

from sldb.api.matching.matcher import Matcher, cosine

__all__ = ["Matcher", "cosine"]
