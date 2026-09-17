"""What belongs to one move and to nothing else (spec 07, 11 §5, spec 13).

Every phase of a move writes to the same trace and the same record — the queries, reads,
writes and edges the MoveDoc will keep — and reads the same few facts about the move being
made: the sentence being said (a pending question and a missing turn remember it), the
creates of this move with an explicit name (spec 06 §Coordinación), and whether the move is
already being understood again because the world moved under it (spec 11 §5). The session
opens one per move and the phases pass it along; nothing in it outlives the move except the
sentence, which the next move starts from.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def _empty_record() -> dict[str, Any]:
    return {"queries": [], "writes": [], "edges": []}


@dataclass
class MoveContext:
    """The trace and record of one move, and what its phases need to know about it."""

    sentence: str = ""
    trace: list[str] = field(default_factory=list)
    record: dict[str, Any] = field(default_factory=_empty_record)
    pending_creates: dict[str, str] = field(default_factory=dict)
    retry: bool = False
