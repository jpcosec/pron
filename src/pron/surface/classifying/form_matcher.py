"""Matching the lexicon's forms against a sentence (spec 06 step 2, spec 05): greedy,
longest form first, and a form's uppercase parts are slots — N (a number), X (free text),
Z (an enum value), DAY and TIME (normalized by pron.surface.dates).
"""

from __future__ import annotations

from typing import Any

from pron.kernel.parts.item import Item
from pron.kernel.parts.word import Word
from pron.surface.classifying.function_word_table import FunctionWordTable
from pron.surface.dates import parse_day, parse_time
from pron.world.lexicon import Lexicon
from pron.world.matching.difflib_matcher import normalize

MAX_FORM_WORDS = 5
SLOTS = {"N", "X", "Z", "DAY", "TIME"}


class FormMatcher:
    """The lexicon's forms, indexed by word count, matched at one position of a sentence."""

    def __init__(self, lex: Lexicon, table: FunctionWordTable, now: Any = None) -> None:
        self.lex = lex
        self.table = table
        self.now = now
        self.forms = self._index_forms()

    def _index_forms(self) -> dict[int, list[tuple[list[str], list[Word]]]]:
        """Forms indexed by word count. A part is a slot only when the alias wrote it in
        uppercase (N, X, Z, DAY, TIME); 'time' as a field name is a plain word."""
        by_len: dict[int, dict[str, list[Word]]] = {}
        for w in self.lex.words:
            parts = [p if p in SLOTS else normalize(p) for p in w.form.split()]
            by_len.setdefault(len(parts), {}).setdefault(" ".join(parts), []).append(w)
        return {n: [(k.split(), ws) for k, ws in d.items()] for n, d in by_len.items()}

    def best(self, toks: list[str], i: int) -> tuple[Item, int] | None:
        """The longest form that matches at `i`, as a word item with its slots and number."""
        for n in range(min(MAX_FORM_WORDS, len(toks) - i), 0, -1):
            for parts, words in self.forms.get(n, []):
                slots = self._match_form(parts, toks[i : i + n])
                if slots is not None:
                    text = " ".join(toks[i : i + n])
                    number = self._number_of(words, text)
                    return Item(
                        "word", text, words=list(words), slots=slots, number=number
                    ), n
        return None

    def _match_form(self, parts: list[str], toks: list[str]) -> dict[str, Any] | None:
        slots: dict[str, Any] = {}
        for p, t in zip(parts, toks):
            if p in SLOTS:
                value = self._slot(p, t)
                if value is None:
                    return None
                slots[p] = value
            elif p != normalize(t):
                return None
        return slots

    def _slot(self, p: str, t: str) -> Any:
        """What a token fills a slot with, or None when it cannot fill it."""
        if p == "N":
            return self.table.number(t) if self.table.is_number(t) else None
        if p in ("Z", "X"):
            return t
        if p == "DAY":
            return parse_day(t, self.now) or None
        return parse_time(t) or None

    @staticmethod
    def _number_of(words: list[Word], text: str) -> str | None:
        nt = normalize(text)
        for w in words:
            if w.kind in ("model", "alias-model"):
                symbol = normalize(w.payload.get("symbol", w.form))
                if nt == symbol or nt == normalize(w.form) and w.kind == "model":
                    return "singular"
                return (
                    "plural"
                    if nt.endswith("s") and not symbol.endswith("s")
                    else "singular"
                )
        return None
