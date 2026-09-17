"""What `Session.turn` does inside its move (spec 06, 13).

A sentence is one of three things. If a question is pending, it is the reply to it. If the
last turn was missing a value and this sentence is a fragment that fits that hole, it is a
correction of that turn, and the corrected sentence runs instead, as a move that says which
one it corrects. Otherwise it is a new sentence. Either way, the hole of the last missing
turn is used up: a correction can only follow the turn it corrects.
"""

from __future__ import annotations

from typing import Any

from pron.kernel.parts.response import Response
from pron.sexpr.turn.collaborator import Collaborator
from pron.sexpr.dialogue.corrector import Corrector
from pron.sexpr.dialogue.replier import Replier


class SentenceTurn(Collaborator):
    """One sentence inside its move: the answer, and the move it refers to, if any."""

    def __call__(
        self, sentence: str, trace: list[str], record: dict[str, Any]
    ) -> tuple[Response, str]:
        if self.s.dialogue.pending is not None:
            return Replier(self.s)(sentence, trace, record)
        corrected = Corrector(self.s)(sentence)
        hole = self.s.dialogue.last_missing
        self.s.dialogue.last_missing = None
        if corrected is None:
            return self.s._new_sentence(sentence, trace, record), ""
        return self._corrected(sentence, corrected, hole, trace, record)

    def _corrected(
        self,
        sentence: str,
        corrected: str,
        hole: dict[str, Any] | None,
        trace: list[str],
        record: dict[str, Any],
    ) -> tuple[Response, str]:
        assert hole is not None
        refers_to = hole.get("move_id", "")
        record["corrects"] = {
            "move": refers_to,
            "fragment": sentence,
            "sentence": corrected,
        }
        trace.append(f"correction of the last missing turn: {corrected!r}")
        return self.s._new_sentence(corrected, trace, record), refers_to
