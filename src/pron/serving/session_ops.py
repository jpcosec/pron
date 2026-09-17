"""The ops that go through a session of the daemon (spec 11 §8, 12 §6): a sentence, a form,
the lexicon, the dialogue state, and closing the session.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pron.serve import Server


class SessionOps:
    """The session ops of one server, each `(name, req, foreign) -> answer`."""

    def __init__(self, server: "Server") -> None:
        self.server = server

    def say(self, name: str, req: dict[str, Any], foreign: bool) -> dict[str, Any]:
        return self._response(self.server.pool.session(name, req, foreign).turn(req["sentence"]))

    def eval(self, name: str, req: dict[str, Any], foreign: bool) -> dict[str, Any]:
        return self._response(self.server.pool.session(name, req, foreign).eval(req["forms"]))

    @staticmethod
    def _response(r: Any) -> dict[str, Any]:
        return {
            "ok": True,
            "text": r.text,
            "outcome": r.outcome,
            "move": r.move_id,
            "trace": r.trace,
            "record": r.record,
        }

    def lexicon(self, name: str, req: dict[str, Any], foreign: bool) -> dict[str, Any]:
        lex = self.server.pool.session(name, req, foreign).lex
        return {"ok": True, "rows": lex.table(req.get("model"))}

    def state(self, name: str, req: dict[str, Any], foreign: bool) -> dict[str, Any]:
        d = self.server.pool.session(name, req, foreign).dialogue
        return {
            "ok": True,
            "state": d.state,
            "singular": d.singular,
            "set": d.last_set,
            "pending": d.pending.kind if d.pending else None,
        }

    def close(self, name: str, req: dict[str, Any], foreign: bool) -> dict[str, Any]:
        return {"ok": True, "closed": self.server.pool.close(name, req)}
