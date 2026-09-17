"""One move (spec 07, 11 §5): whatever a turn does, bracketed and recorded.

A move opens an sldb operation, reads hash_mundo (reloading the lexicon and projection if
the world changed outside pron), runs the turn, and writes the MoveDoc: who said what, the
outcome, the dialogue state before and after, hash_mundo before and after, the move it
refers to, and the full record — queries, reads, writes, edges and the trace. A StoreError
anywhere in the turn is an answer, not a crash, and it is recorded like any other outcome.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Callable

from pron.kernel.parts.response import Response
from pron.world.store_error import StoreError

if TYPE_CHECKING:
    from pron.sexpr.turn.move_context import MoveContext
    from pron.sexpr.turn.projection_state import ProjectionState

Body = Callable[["MoveContext"], tuple[Response, str]]


class Move:
    """A turn's body, run inside a move, and the move written to the ledger."""

    def __init__(self, state: ProjectionState):
        self.state = state
        self.dialogue, self.ledger = state.dialogue, state.ledger

    def __call__(self, said: str, ctx: MoveContext, body: Body) -> Response:
        self.state.world.store.begin_operation()
        self.at = datetime.now(timezone.utc).replace(microsecond=0)
        self.move_id = self.ledger.new_id(self.at)
        self.state_before = self.dialogue.state
        self.ctx = ctx
        self.hash_before = self.state.sync(ctx.trace)
        resp, refers_to = self._run(body)
        self._settle(resp)
        return self._log(said, resp, refers_to)

    def _run(self, body: Body) -> tuple[Response, str]:
        try:
            return body(self.ctx)
        except StoreError as e:
            self.ctx.record["error"] = str(e)
            return Response(f"Could not do that: {e}", "error"), ""

    def _settle(self, resp: Response) -> None:
        """What the turn leaves behind it: the hole to correct, the hash, no warnings —
        on the kernel as the projection is loaded now, which the turn may have reloaded."""
        if resp.outcome == "missing" and self.dialogue.last_missing is not None:
            self.dialogue.last_missing["move_id"] = self.move_id
        writes = self.ctx.record["writes"]
        self.hash_after = self.state.world.hash_mundo() if writes else self.hash_before
        if writes:
            self.state.tools.kernel.warnings = []

    def _log(self, said: str, resp: Response, refers_to: str) -> Response:
        record = self.ctx.record
        record["interpretation"] = record.get("interpretation", {})
        record["trace"] = list(self.ctx.trace)
        self.ledger.write(
            move_id=self.move_id,
            at=self.at,
            speaker=self.dialogue.speaker,
            sentence=said,
            outcome=resp.outcome,
            state_before=self.state_before,
            state_after=self.dialogue.state,
            hash_before=self.hash_before,
            hash_after=self.hash_after,
            refers_to=refers_to,
            record=record,
        )
        return self._answer(resp)

    def _answer(self, resp: Response) -> Response:
        self.state.hash = self.hash_after
        resp.trace = self.ctx.trace
        resp.move_id = self.move_id
        resp.record = self.ctx.record
        return resp
