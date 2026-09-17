"""The existing values of a field, ranked against a text that did not match (spec 05 §Calce
aproximado). The projection's `matching` says how many neighbors to offer, from what score,
and how many distinct values a field may have before it is too wide to rank — which the trace
then says. Both value suggestions, for a predicate that missed (PLAN 11 P1) and for an unknown
word (P2), rank through this.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pron.world.lexicon import Lexicon
    from pron.world.matching.matcher import Matcher


@dataclass(frozen=True)
class FieldValues:
    lex: Lexicon
    matcher: Matcher
    max_values: int
    neighbors: int
    threshold: float

    @classmethod
    def of(
        cls, projection: dict[str, Any], lex: Lexicon, matcher: Matcher
    ) -> FieldValues:
        matching = projection.get("matching") or {}
        return cls(
            lex,
            matcher,
            int(matching.get("max_values", 500)),
            int(matching.get("neighbors", 3)),
            float(matching.get("threshold", 0.55)),
        )

    def rankable(
        self, model: str, name: str, trace: list[str], prose: bool = True
    ) -> list[str]:
        """The field's distinct values, or none when there are none, when they are free prose
        (unless `prose`) or when there are too many to rank — and then the trace says so."""
        values = self.lex.distinct_values(model, name)
        if not values or (not prose and _is_prose(values)):
            return []
        if len(values) > self.max_values:
            trace.append(
                f"{model}.{name}: {len(values)} distinct values over "
                f"matching.max_values ({self.max_values}), no value suggestion"
            )
            return []
        return values

    def rank(self, text: str, values: list[str]) -> list[tuple[str, float]]:
        return self.matcher.rank(
            text, [(v, v) for v in values], k=self.neighbors, threshold=self.threshold
        )


def _is_prose(values: list[str]) -> bool:
    """Free prose (a statement, a note), not a nameable value one word says."""
    return any(len(v.split()) > 6 for v in values)
