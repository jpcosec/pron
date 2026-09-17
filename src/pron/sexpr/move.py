"""One move (spec 07, 11 §5): whatever a turn does, bracketed and recorded.

A move opens an sldb operation, reads hash_mundo (reloading the lexicon and projection if
the world changed outside pron), runs the turn, and writes the MoveDoc: who said what, the
outcome, the dialogue state before and after, hash_mundo before and after, the move it
refers to, and the full record — queries, reads, writes, edges and the trace. A StoreError
anywhere in the turn is an answer, not a crash, and it is recorded like any other outcome.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable

from pron.kernel.response import Response
from pron.sexpr.collaborator import Collaborator
from pron.world.store_error import StoreError

Body = Callable[[list[str], dict[str, Any]], tuple[Response, str]]


class Move(Collaborator):
    """A turn's body, run inside a move, and the move written to the ledger."""

    def __call__(self, said: str, body: Body) -> Response:
        self.s.world.store.begin_operation()
        self.at = datetime.now(timezone.utc).replace(microsecond=0)
        self.move_id = self.s.ledger.new_id(self.at)
        self.state_before = self.s.dialogue.state
        self.trace: list[str] = []
        self.record: dict[str, Any] = {"queries": [], "writes": [], "edges": []}
        self.hash_before = self.s._sync(self.trace)
        resp, refers_to = self._run(body)
        self._settle(resp)
        return self._log(said, resp, refers_to)

    def _run(self, body: Body) -> tuple[Response, str]:
        try:
            return body(self.trace, self.record)
        except StoreError as e:
            self.record["error"] = str(e)
            return Response(f"Could not do that: {e}", "error"), ""

    def _settle(self, resp: Response) -> None:
        """What the turn leaves behind it: the hole to correct, the hash, no warnings."""
        if resp.outcome == "missing" and self.s.dialogue.last_missing is not None:
            self.s.dialogue.last_missing["move_id"] = self.move_id
        writes = self.record["writes"]
        self.hash_after = self.s.world.hash_mundo() if writes else self.hash_before
        if writes:
            self.s.kernel.warnings = []

    def _log(self, said: str, resp: Response, refers_to: str) -> Response:
        self.record["interpretation"] = self.record.get("interpretation", {})
        self.record["trace"] = list(self.trace)
        self.s.ledger.write(
            move_id=self.move_id,
            at=self.at,
            speaker=self.s.dialogue.speaker,
            sentence=said,
            outcome=resp.outcome,
            state_before=self.state_before,
            state_after=self.s.dialogue.state,
            hash_before=self.hash_before,
            hash_after=self.hash_after,
            refers_to=refers_to,
            record=self.record,
        )
        return self._answer(resp)

    def _answer(self, resp: Response) -> Response:
        self.s.hash = self.hash_after
        resp.trace = self.trace
        resp.move_id = self.move_id
        resp.record = self.record
        return resp
