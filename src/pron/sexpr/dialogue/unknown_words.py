"""A word this projection does not have (spec 05 §Calce aproximado, spec 06).

Nothing is guessed and nothing is run. The lexicon's nearest words are offered, and if none
of them is a value, the existing values of the world are ranked too and offered as the
sentence that would resolve. The trace says which matcher decided and what it found, so an
answer nobody expected can be explained without running anything again.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.parts.interpretation import Interpretation
from pron.kernel.parts.response import Response
from pron.sexpr.dialogue.parse_hint import cannot_parse_hint

if TYPE_CHECKING:
    from pron.sexpr.dialogue.value_suggestions import ValueSuggestions
    from pron.sexpr.turn.move_context import MoveContext
    from pron.world.lexicon import Lexicon
    from pron.world.matching.matcher import Matcher

Suggestion = tuple[str, str, str, str]


class UnknownWords:
    """What to say back about the first word of a sentence that is not in the lexicon."""

    def __init__(self, lex: Lexicon, matcher: Matcher, suggestions: ValueSuggestions):
        self.lex, self.matcher, self.suggestions = lex, matcher, suggestions

    def __call__(self, interp: Interpretation, ctx: MoveContext) -> Response:
        word = interp.unknown[0].text
        near = self.lex.near(word)
        values = self._values(word, near, ctx.trace)
        self._record(word, near, values, ctx.record)
        names = [f"*{w.form}*" for w, _ in near]
        ctx.trace.append(self._line(word, names, values))
        return self._answer(word, [f"*{s}*" for *_, s in values] + names)

    def _values(
        self, word: str, near: list, trace: list[str]
    ) -> list[Suggestion]:
        """Values are only ranked when no near word is one already."""
        if any(w.kind == "value" for w, _ in near):
            return []
        return self.suggestions(word, trace)

    def _record(
        self,
        word: str,
        near: list,
        values: list[Suggestion],
        record: dict[str, Any],
    ) -> None:
        record["missing"] = {
            "word": word,
            "near": [w.form for w, _ in near],
            "matcher": self.matcher.id(),
        }
        if values:
            record["missing"]["values"] = [
                {"model": m, "field": f, "value": v, "sentence": sent}
                for m, f, v, sent in values
            ]

    def _line(self, word: str, names: list[str], values: list[Suggestion]) -> str:
        return (
            f"'{word}' is not in the projection · near ({self.matcher.id()}): "
            f"{', '.join(names) or 'nothing'}"
            + (
                "; value candidates: " + ", ".join(sent for *_, sent in values)
                if values
                else ""
            )
        )

    def _answer(self, word: str, offers: list[str]) -> Response:
        return Response(
            f'I don\'t have "{word}".'
            + (
                f" Did you mean {' or '.join(offers)}?"
                if offers
                else " " + cannot_parse_hint(self.lex)
            ),
            "missing",
        )
