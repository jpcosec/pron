"""Running a compiled write (spec 14 §4, §5): the ladder first, then the form — evaluated
with `session.eval` (verbs, pre-validation, writes, refresh, MoveDoc, undo), or with
`dry_run` only pre-validated — and the answer as JSON.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from pron.mcp.writes.arg_error import ArgError
from pron.mcp.writes.dry_move import DryMove
from pron.mcp.writes.ladder import Ladder
from pron.mcp.writes.response_json import response_json

if TYPE_CHECKING:
    from pron.session import Session


class FormRunner:
    """One session's write tools go through here."""

    def __init__(self, session: Session):
        self.session = session
        self.ladder = Ladder(session)

    def __call__(
        self, level: int, compile: Callable[[], str], dry_run: bool = False
    ) -> dict[str, Any]:
        """`compile` builds the form once the level allows it; arguments that make no form
        are an error before anything is evaluated."""
        refused = self.ladder.requires(level)
        if refused is not None:
            return refused
        try:
            forms = compile()
        except ArgError as e:
            return {"text": str(e), "outcome": "error", "move_id": "", "writes": []}
        return self.run(forms, dry_run)

    def run(self, forms: str, dry_run: bool = False) -> dict[str, Any]:
        resp = DryMove(self.session)(forms) if dry_run else self.session.eval(forms)
        return response_json(resp, dry_run)
