"""PLAN 11 P2 (spec 05 §Calce aproximado): an unknown word ranked against real values.

When an unknown word has no vocabulary neighbor of kind 'value', it is ranked against the
existing values of every string, non-enum field of this projection's models, and what is
offered is the sentence that would resolve — 'the <model> <alias-field or field> <value>' —
so the candidate is usable as said. Free prose is not a nameable value and is skipped; a
field with more distinct values than matching.max_values is too wide to rank and says so in
the trace. Same cap as P1; this never executes anything on its own.
"""

from __future__ import annotations

from typing import Any

from pron.sexpr.turn.collaborator import Collaborator
from pron.world.lexicon import UNSUGGESTED_MODELS

Scored = tuple[float, str, str, str, str]
Suggestion = tuple[str, str, str, str]


class ValueSuggestions(Collaborator):
    """The sentences an unknown word could have meant, best first."""

    def __call__(self, word: str, trace: list[str]) -> list[Suggestion]:
        matching = self.s.projection.get("matching") or {}
        self.max_values = int(matching.get("max_values", 500))
        self.neighbors = int(matching.get("neighbors", 3))
        self.threshold = float(matching.get("threshold", 0.55))
        scored: list[Scored] = []
        for model in self.s.lex.models:
            if model not in UNSUGGESTED_MODELS:
                scored += self._model(word, model, trace)
        scored.sort(key=lambda t: -t[0])
        return self._best(scored)

    def _model(self, word: str, model: str, trace: list[str]) -> list[Scored]:
        out: list[Scored] = []
        for f in self.s.world.schema(model, self.s.lex.stores):
            if f["kind"] == "string":
                out += self._field(word, model, f["name"], trace)
        return out

    def _field(
        self, word: str, model: str, name: str, trace: list[str]
    ) -> list[Scored]:
        values = self._values(model, name, trace)
        if not values:
            return []
        return [
            (score, model, name, value, self._sentence(model, name, value))
            for value, score in self._rank(word, values)
        ]

    def _values(self, model: str, name: str, trace: list[str]) -> list[str]:
        values = self.s.lex.distinct_values(model, name)
        if not values or _is_prose(values):
            return []
        if len(values) > self.max_values:
            trace.append(
                f"{model}.{name}: {len(values)} distinct values over "
                f"matching.max_values ({self.max_values}), no value suggestion"
            )
            return []
        return values

    def _rank(self, word: str, values: list[str]) -> list[tuple[str, float]]:
        return self.s.matcher.rank(
            word, [(v, v) for v in values], k=self.neighbors, threshold=self.threshold
        )

    def _sentence(self, model: str, name: str, value: Any) -> str:
        """What someone would have to say for this value to resolve."""
        return (
            f"the {self.s.lex.model_form(model)} "
            f"{self.s.lex.field_form(model, name)} {value}"
        )

    def _best(self, scored: list[Scored]) -> list[Suggestion]:
        out: list[Suggestion] = []
        seen: set[str] = set()
        for _, model, fname, value, sentence in scored:
            if sentence in seen:
                continue
            seen.add(sentence)
            out.append((model, fname, value, sentence))
            if len(out) >= self.neighbors:
                break
        return out


def _is_prose(values: list[str]) -> bool:
    """Free prose (a statement, a note), not a nameable value one word says."""
    return any(len(v.split()) > 6 for v in values)
