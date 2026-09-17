"""Classifying a sentence against the lexicon (spec 06 steps 1–2).

A sentence becomes a list of items. Each item is one of: `det`, `referent`, `wh`,
`conj`, `punct`, `number`, `literal`, `word` (one or more lexicon words sharing the
matched form, ambiguity kept), or `unknown`. Matching is greedy longest-first over
listed forms; forms may carry slots: N (a number), X (free text up to the next known
word), Z (an enum value), DAY and TIME (normalized by pron.surface.dates).
"""

from __future__ import annotations

from typing import Any

from pron.kernel.item import Item
from pron.kernel.word import Word
from pron.surface.dates import parse_day, parse_time
from pron.surface.tokens import tokenize
from pron.world.difflib_matcher import normalize
from pron.world.lexicon import FUNCTION_WORDS, Lexicon

MAX_FORM_WORDS = 5
SLOTS = {"N", "X", "Z", "DAY", "TIME"}


class Classifier:
    def __init__(self, lexicon: Lexicon, now: Any = None):
        self.lex = lexicon
        self.now = now
        fw = FUNCTION_WORDS
        self.function: dict[str, tuple[str, dict]] = {}
        for num, forms in fw["determiners"].items():
            for f in forms:
                self.function[normalize(f)] = (
                    "det",
                    {"number": num if f != "the" else None},
                )
        for num, forms in fw["referents"].items():
            for f in forms:
                self.function[normalize(f)] = (
                    "referent",
                    {"number": "plural" if num == "plural" else "singular", "who": num},
                )
        for kind, forms in fw["interrogatives"].items():
            for f in forms:
                self.function.setdefault(normalize(f), ("wh", {"question": kind}))
        for f in fw["conjunction"]:
            self.function[normalize(f)] = ("conj", {})
        for f in fw["negation"]:
            self.function[normalize(f)] = ("negation", {})
        for f in fw["preposition_of"]:
            self.function[normalize(f)] = ("of", {})
        self.numbers = {k: v for k, v in fw["numbers"]["words"].items()}
        self.lexicon_forms = self._index_forms()

    def _index_forms(self) -> dict[int, list[tuple[list[str], list[Word]]]]:
        """Forms indexed by word count. A part is a slot only when the alias wrote it in
        uppercase (N, X, Z, DAY, TIME); 'time' as a field name is a plain word."""
        by_len: dict[int, dict[str, list[Word]]] = {}
        for w in self.lex.words:
            parts = [p if p in SLOTS else normalize(p) for p in w.form.split()]
            by_len.setdefault(len(parts), {}).setdefault(" ".join(parts), []).append(w)
        return {n: [(k.split(), ws) for k, ws in d.items()] for n, d in by_len.items()}

    # -- public --------------------------------------------------------------------

    def classify(self, sentence: str) -> list[Item]:
        toks = tokenize(sentence)
        items: list[Item] = []
        i = 0
        while i < len(toks):
            item, used = self._match_at(toks, i)
            items.append(item)
            i += used
        return items

    # -- matching --------------------------------------------------------------------

    def _match_at(self, toks: list[str], i: int) -> tuple[Item, int]:
        t = toks[i]
        if t.startswith('"') and t.endswith('"') and len(t) >= 2:
            return Item("literal", t[1:-1], meta={"quoted": True}), 1
        if t in ("?", ",", ".", ":", ";", "!"):
            return Item("punct", t), 1
        if t.endswith(":") and normalize(t[:-1]) in (
            "to",
            "saying",
            "note",
            "named",
            "called",
        ):
            lit, used = self._literal_after(toks, i + 1)
            return Item("literal", lit, meta={"marker": t}), 1 + used
        best = self._best_lexicon_match(toks, i)
        fn = self._function_match(toks, i)
        if fn and (best is None or fn[1] >= best[1]):
            return fn[0], fn[1]
        if best:
            return best[0], best[1]
        if self._is_number(t):
            return Item("number", t, meta={"value": self._number(t)}), 1
        day = parse_day(t, self.now)
        if day:
            return Item("literal", t, meta={"kind": "date", "value": day}), 1
        return Item("unknown", t), 1

    def _function_match(self, toks: list[str], i: int) -> tuple[Item, int] | None:
        for n in range(min(4, len(toks) - i), 0, -1):
            span = normalize(" ".join(toks[i : i + n]))
            if span in self.function:
                kind, meta = self.function[span]
                return Item(
                    kind,
                    " ".join(toks[i : i + n]),
                    number=meta.get("number"),
                    meta=meta,
                ), n
        return None

    def _best_lexicon_match(self, toks: list[str], i: int) -> tuple[Item, int] | None:
        for n in range(min(MAX_FORM_WORDS, len(toks) - i), 0, -1):
            for parts, words in self.lexicon_forms.get(n, []):
                slots = self._match_form(parts, toks[i : i + n], words)
                if slots is not None:
                    text = " ".join(toks[i : i + n])
                    number = self._number_of(words, text)
                    return Item(
                        "word", text, words=list(words), slots=slots, number=number
                    ), n
        return None

    def _match_form(
        self, parts: list[str], toks: list[str], words: list[Word]
    ) -> dict[str, Any] | None:
        slots: dict[str, Any] = {}
        for p, t in zip(parts, toks):
            nt = normalize(t)
            if p == "N":
                if not self._is_number(t):
                    return None
                slots["N"] = self._number(t)
            elif p == "Z":
                slots["Z"] = t
            elif p == "X":
                slots["X"] = t
            elif p == "DAY":
                d = parse_day(t, self.now)
                if not d:
                    return None
                slots["DAY"] = d
            elif p == "TIME":
                tm = parse_time(t)
                if not tm:
                    return None
                slots["TIME"] = tm
            elif p != nt:
                return None
        return slots

    def _literal_after(self, toks: list[str], j: int) -> tuple[str, int]:
        out = []
        k = j
        while (
            k < len(toks)
            and toks[k] not in ("?", ".", ";", "!")
            and normalize(toks[k]) != "and"
        ):
            out.append(toks[k].strip('"'))
            k += 1
        return " ".join(out), k - j

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

    def _is_number(self, t: str) -> bool:
        return t.isdigit() or normalize(t) in self.numbers

    def _number(self, t: str) -> int:
        return int(t) if t.isdigit() else int(self.numbers[normalize(t)])
