"""pron's function words as the classifier matches them (spec 06 steps 1–2, spec 05):
determiners, referents, interrogatives, the conjunction, negation and "of", by normalized
form, with the number or question each one carries; and the number words.
"""

from __future__ import annotations

from typing import Any

from pron.world.lexicon import FUNCTION_WORDS
from pron.world.matching.difflib_matcher import normalize


class FunctionWordTable:
    """normalized form -> (item kind, meta), and the number words, from function_words.yaml."""

    def __init__(self, fw: dict[str, Any] = FUNCTION_WORDS) -> None:
        self.function: dict[str, tuple[str, dict]] = {}
        self._determiners(fw["determiners"])
        self._referents(fw["referents"])
        for kind, forms in fw["interrogatives"].items():
            for f in forms:
                self.function.setdefault(normalize(f), ("wh", {"question": kind}))
        for key, kind in (
            ("conjunction", "conj"),
            ("negation", "negation"),
            ("preposition_of", "of"),
        ):
            for f in fw[key]:
                self.function[normalize(f)] = (kind, {})
        self.numbers = {k: v for k, v in fw["numbers"]["words"].items()}

    def _determiners(self, determiners: dict[str, list[str]]) -> None:
        """ "the" carries no number: the noun form that follows decides it."""
        for num, forms in determiners.items():
            for f in forms:
                self.function[normalize(f)] = (
                    "det",
                    {"number": num if f != "the" else None},
                )

    def _referents(self, referents: dict[str, list[str]]) -> None:
        for num, forms in referents.items():
            for f in forms:
                self.function[normalize(f)] = (
                    "referent",
                    {"number": "plural" if num == "plural" else "singular", "who": num},
                )

    def is_number(self, t: str) -> bool:
        return t.isdigit() or normalize(t) in self.numbers

    def number(self, t: str) -> int:
        return int(t) if t.isdigit() else int(self.numbers[normalize(t)])
