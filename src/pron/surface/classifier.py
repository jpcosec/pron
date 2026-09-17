"""Classifying a sentence against the lexicon (spec 06 steps 1–2).

A sentence becomes a list of items. Each item is one of: `det`, `referent`, `wh`,
`conj`, `punct`, `number`, `literal`, `word` (one or more lexicon words sharing the
matched form, ambiguity kept), or `unknown`. Matching is greedy longest-first over
listed forms; forms may carry slots: N (a number), X (free text up to the next known
word), Z (an enum value), DAY and TIME (normalized by pron.surface.dates).

The function words are a `FunctionWordTable` and the lexicon's forms a `FormMatcher`, both
in pron.surface.classifying.
"""

from __future__ import annotations

from typing import Any

from pron.kernel.parts.item import Item
from pron.surface.classifying.form_matcher import FormMatcher
from pron.surface.classifying.function_word_table import FunctionWordTable
from pron.surface.dates import parse_day
from pron.surface.tokens import tokenize
from pron.world.lexicon import Lexicon
from pron.world.matching.difflib_matcher import normalize

PUNCT = ("?", ",", ".", ":", ";", "!")
MARKERS = ("to", "saying", "note", "named", "called")


class Classifier:
    def __init__(self, lexicon: Lexicon, now: Any = None):
        self.lex = lexicon
        self.now = now
        self.table = FunctionWordTable()
        self.forms = FormMatcher(lexicon, self.table, now)

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
        marked = self._marked(toks, i)
        if marked is not None:
            return marked
        best = self.forms.best(toks, i)
        fn = self._function_match(toks, i)
        if fn and (best is None or fn[1] >= best[1]):
            return fn[0], fn[1]
        if best:
            return best[0], best[1]
        return self._unlisted(toks[i]), 1

    def _marked(self, toks: list[str], i: int) -> tuple[Item, int] | None:
        """A quoted literal, punctuation, or a literal after a marker ("saying: …")."""
        t = toks[i]
        if t.startswith('"') and t.endswith('"') and len(t) >= 2:
            return Item("literal", t[1:-1], meta={"quoted": True}), 1
        if t in PUNCT:
            return Item("punct", t), 1
        if t.endswith(":") and normalize(t[:-1]) in MARKERS:
            lit, used = self._literal_after(toks, i + 1)
            return Item("literal", lit, meta={"marker": t}), 1 + used
        return None

    def _unlisted(self, t: str) -> Item:
        """A token no form matched: a number, a date, or unknown."""
        if self.table.is_number(t):
            return Item("number", t, meta={"value": self.table.number(t)})
        day = parse_day(t, self.now)
        if day:
            return Item("literal", t, meta={"kind": "date", "value": day})
        return Item("unknown", t)

    def _function_match(self, toks: list[str], i: int) -> tuple[Item, int] | None:
        for n in range(min(4, len(toks) - i), 0, -1):
            span = normalize(" ".join(toks[i : i + n]))
            if span in self.table.function:
                kind, meta = self.table.function[span]
                return Item(
                    kind,
                    " ".join(toks[i : i + n]),
                    number=meta.get("number"),
                    meta=meta,
                ), n
        return None

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
