"""PLAN 11 P2 (spec 05 §Calce aproximado): an unknown word ranked against real values.

When an unknown word has no vocabulary neighbor of kind 'value', it is ranked against the
existing values of every string, non-enum field of this projection's models, and what is
offered is the sentence that would resolve — 'the <model> <alias-field or field> <value>' —
so the candidate is usable as said. Free prose is not a nameable value and is skipped; a
field with more distinct values than matching.max_values is too wide to rank and says so in
the trace. Same cap as P1 (pron.sexpr.resolving.field_values); this never executes anything
on its own.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.sexpr.resolving.field_values import FieldValues
from pron.world.doc_kind import kind_of

if TYPE_CHECKING:
    from pron.world.lexicon import Lexicon
    from pron.world.matching.matcher import Matcher
    from pron.world.world import World

Scored = tuple[float, str, str, str, str]
Suggestion = tuple[str, str, str, str]


class ValueSuggestions:
    """The sentences an unknown word could have meant, best first."""

    def __init__(
        self, projection: dict[str, Any], lex: Lexicon, world: World, matcher: Matcher
    ):
        self.projection, self.lex, self.world, self.matcher = (
            projection,
            lex,
            world,
            matcher,
        )

    def __call__(self, word: str, trace: list[str]) -> list[Suggestion]:
        self.values = FieldValues.of(self.projection, self.lex, self.matcher)
        scored: list[Scored] = []
        for model in self.lex.models:
            if kind_of(model).suggests_values:
                scored += self._model(word, model, trace)
        scored.sort(key=lambda t: -t[0])
        return self._best(scored)

    def _model(self, word: str, model: str, trace: list[str]) -> list[Scored]:
        out: list[Scored] = []
        for f in self.world.schema(model, self.lex.stores):
            if f["kind"] == "string":
                out += self._field(word, model, f["name"], trace)
        return out

    def _field(
        self, word: str, model: str, name: str, trace: list[str]
    ) -> list[Scored]:
        values = self.values.rankable(model, name, trace, prose=False)
        if not values:
            return []
        return [
            (score, model, name, value, self._sentence(model, name, value))
            for value, score in self.values.rank(word, values)
        ]

    def _sentence(self, model: str, name: str, value: Any) -> str:
        """What someone would have to say for this value to resolve."""
        return (
            f"the {self.lex.model_form(model)} "
            f"{self.lex.field_form(model, name)} {value}"
        )

    def _best(self, scored: list[Scored]) -> list[Suggestion]:
        out: list[Suggestion] = []
        seen: set[str] = set()
        for _, model, fname, value, sentence in scored:
            if sentence in seen:
                continue
            seen.add(sentence)
            out.append((model, fname, value, sentence))
            if len(out) >= self.values.neighbors:
                break
        return out
