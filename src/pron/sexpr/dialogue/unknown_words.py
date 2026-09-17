"""A word this projection does not have (spec 05 §Calce aproximado, spec 06).

Nothing is guessed and nothing is run. The lexicon's nearest words are offered, and if none
of them is a value, the existing values of the world are ranked too and offered as the
sentence that would resolve. The trace says which matcher decided and what it found, so an
answer nobody expected can be explained without running anything again.
"""

from __future__ import annotations

from typing import Any

from pron.kernel.parts.interpretation import Interpretation
from pron.kernel.parts.response import Response
from pron.sexpr.turn.collaborator import Collaborator
from pron.sexpr.dialogue.parse_hint import cannot_parse_hint

Suggestion = tuple[str, str, str, str]


class UnknownWords(Collaborator):
    """What to say back about the first word of a sentence that is not in the lexicon."""

    def __call__(
        self, interp: Interpretation, trace: list[str], record: dict[str, Any]
    ) -> Response:
        word = interp.unknown[0].text
        near = self.s.lex.near(word)
        values = self._values(word, near, trace)
        self._record(word, near, values, record)
        names = [f"*{w.form}*" for w, _ in near]
        trace.append(self._line(word, names, values))
        return self._answer(word, [f"*{s}*" for *_, s in values] + names)

    def _values(
        self, word: str, near: list, trace: list[str]
    ) -> list[Suggestion]:
        """Values are only ranked when no near word is one already."""
        if any(w.kind == "value" for w, _ in near):
            return []
        return self.s._value_word_suggestions(word, trace)

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
            "matcher": self.s.matcher.id(),
        }
        if values:
            record["missing"]["values"] = [
                {"model": m, "field": f, "value": v, "sentence": sent}
                for m, f, v, sent in values
            ]

    def _line(self, word: str, names: list[str], values: list[Suggestion]) -> str:
        return (
            f"'{word}' is not in the projection · near ({self.s.matcher.id()}): "
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
                else " " + cannot_parse_hint(self.s.lex)
            ),
            "missing",
        )
