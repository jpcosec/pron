"""Every write tool of levels 1 and 2 over one session (spec 14 §4): what the MCP wiring
holds per `(world, speaker)` session and calls, one method per tool."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pron.mcp.writes.content_writes import ContentWrites
from pron.mcp.writes.ladder import Ladder
from pron.mcp.writes.rule_writes import RuleWrites

if TYPE_CHECKING:
    from pron.session import Session


class Writes(ContentWrites, RuleWrites):
    """The level-1 and level-2 tools of one session, and its level."""

    def __init__(self, session: Session):
        ContentWrites.__init__(self, session)
        self.ladder = Ladder(session)

    @property
    def level(self) -> int:
        return self.ladder.level
