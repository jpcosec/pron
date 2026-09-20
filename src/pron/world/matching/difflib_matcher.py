"""The no-network fallback of the approximate-matching port, re-exported from sldb
(spec 11 §2): difflib over accent-stripped strings, and `normalize`, that stripping.
"""

from __future__ import annotations

from sldb.api.matching.difflib_matcher import DifflibMatcher, normalize

__all__ = ["DifflibMatcher", "normalize"]
