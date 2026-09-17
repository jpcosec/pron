"""What the determiner makes of the addresses a noun phrase resolved to (spec 02, 05): one is
unique; several are ambiguous, unless the phrase said any; none is missing, and then what is
offered is the nearest existing value of an equality predicate that missed (PLAN 11 P1, spec
05 §Calce aproximado) or else the documents nearest to its proper names. A plural phrase is
whatever it found. Values are only offered, never entered as lexicon nor executed.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from pron.kernel.parts.noun_phrase import NounPhrase
from pron.sexpr.resolving.field_kind import field_kind
from pron.sexpr.resolving.field_values import FieldValues
from pron.sexpr.resolving.resolution import Resolution

if TYPE_CHECKING:
    from pron.sexpr.resolving.proper_names import ProperNames
    from pron.world.lexicon import Lexicon

_EQ_PREDICATE = re.compile(r'^(\w+)\s*=\s*"([^"]*)"$')
NearValue = tuple[str, str, str, list[str]]


class Decision:
    """The outcome of one resolution: unique, ambiguous or missing."""

    def __init__(self, lex: Lexicon, names: ProperNames):
        self.lex, self.names = lex, names

    def __call__(
        self, np: NounPhrase, result: list[str], queries: list[str]
    ) -> Resolution:
        assert np.model is not None
        if not result and np.proper:
            # a proper name that is not the doc name: try name/title fields, then offer neighbors
            result = self.names.by_name_fields(np, queries) or result
        if np.number != "singular" or len(result) == 1:
            return Resolution(np, result, "unico", queries)
        if len(result) > 1 and np.determiner == "any":
            note = f"any: took {result[0]}; also {', '.join(result[1:])}"
            return Resolution(
                np, result[:1], "unico", queries, candidates=result[1:], note=note
            )
        if len(result) > 1:
            return Resolution(np, [], "ambiguo", queries, candidates=result)
        return self._missing(np, queries)

    def _missing(self, np: NounPhrase, queries: list[str]) -> Resolution:
        values = FieldValues.of(self.lex.projection, self.lex, self.lex.matcher)
        hit = self._near_value(np, values, queries)
        if hit is not None:
            model, fld, text, candidates = hit
            np.unknown_values.append((model, fld, text))
        else:
            candidates = self.names.near(np, values.threshold)
        note = f"no {np.model} matches {np.describe()}"
        return Resolution(np, [], "missing", queries, candidates=candidates, note=note)

    def _near_value(
        self, np: NounPhrase, values: FieldValues, queries: list[str]
    ) -> NearValue | None:
        """For each equality predicate on a string, non-enum field, the text that did not match
        ranked against the field's existing distinct values (family included, stores of the
        projection): (model, field, text, ranked) for the first predicate with a hit."""
        assert np.model is not None
        for where in np.predicates:
            m = _EQ_PREDICATE.match(where)
            if not m or field_kind(self.lex, np.model, m.group(1)) != "string":
                continue
            fld, text = m.group(1), m.group(2)
            existing = values.rankable(np.model, fld, queries)
            ranked = [key for key, _ in values.rank(text, existing)] if existing else []
            if ranked:
                return np.model, fld, text, ranked
        return None
