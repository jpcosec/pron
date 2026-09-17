"""The no-network fallback of the approximate-matching port (spec 11 §2): difflib over
accent-stripped strings. `normalize` is that stripping, and is also how the lexicon and the
classifier compare a written word with a listed form (spec 05, 06).
"""

from __future__ import annotations

import unicodedata
from difflib import SequenceMatcher


def normalize(text: str) -> str:
    stripped = "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )
    return " ".join(stripped.lower().split())


class DifflibMatcher:
    """Fallback similarity: the best SequenceMatcher ratio between the query and the
    candidate string or any of its words."""

    def id(self) -> str:
        return "difflib"

    def similarity(self, query: str, candidate: str) -> float:
        q, c = normalize(query), normalize(candidate)
        if not q or not c:
            return 0.0
        best = SequenceMatcher(None, q, c).ratio()
        for word in c.split():
            best = max(best, SequenceMatcher(None, q, word).ratio())
        return best
