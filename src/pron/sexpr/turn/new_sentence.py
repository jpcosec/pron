"""A new sentence (spec 13, 05): the surface says it as forms and the forms are evaluated.

The surface only interprets. A sentence made only of words the projection does not have,
or of nouns among them, is answered with what the lexicon has near it; a sentence with any
part nobody could parse is answered with sentences this world does understand. Anything
else is said as forms, and the forms are what gets resolved and run — so a sentence and the
forms it says leave exactly the same move. If the world changes while the move is being
understood, the sentence itself is understood again, not the forms it said the first time.
"""

from __future__ import annotations

from typing import Any

from pron.kernel.parts.interpretation import Interpretation
from pron.kernel.parts.response import Response
from pron.sexpr.turn.collaborator import Collaborator
from pron.sexpr.dialogue.parse_hint import cannot_parse_hint
from pron.sexpr.dialogue.unknown_words import UnknownWords
from pron.surface.render import said


class NewSentence(Collaborator):
    """One sentence that does not answer a pending question, understood and run."""

    def __call__(
        self,
        sentence: str,
        trace: list[str],
        record: dict[str, Any],
        retry: bool = False,
    ) -> Response:
        self.s._sentence = sentence
        interp = self.s.interpreter.interpret(sentence)
        record["interpretation"] = interp.to_record()
        trace.append("interpretation: " + interp.forma)
        unclear = self._unclear(interp, trace, record)
        if unclear is not None:
            return unclear
        return self._evaluate(sentence, interp, trace, record, retry)

    def _evaluate(
        self,
        sentence: str,
        interp: Interpretation,
        trace: list[str],
        record: dict[str, Any],
        retry: bool,
    ) -> Response:
        """The forms the sentence says; if the world moves meanwhile, the sentence again."""
        return self.s._eval(
            said(interp.parts, self.s),
            trace,
            record,
            retry=retry,
            again=lambda: self.s._new_sentence(sentence, trace, record, retry=True),
        )

    def _unclear(
        self, interp: Interpretation, trace: list[str], record: dict[str, Any]
    ) -> Response | None:
        if interp.unknown and all(p.kind in ("none", "nominal") for p in interp.parts):
            return UnknownWords(self.s)(interp, trace, record)
        if any(p.kind == "none" for p in interp.parts):
            return Response(cannot_parse_hint(self.s.lex), "missing")
        return None
