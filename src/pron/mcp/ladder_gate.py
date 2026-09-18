"""The ladder of mutability at the tool table's door (spec 14 §5): a tool of a level higher
than the session of `(world, speaker)` answers the ladder's error without running. Level-0
tools always pass, and open no session.
"""

from __future__ import annotations

from typing import Any

from pron.mcp.tool_table import ToolSpec
from pron.mcp.world_mounts import WorldMounts
from pron.mcp.writes.ladder import Ladder


class LadderGate:
    """`ToolTable.gate`: the session's level against the tool's."""

    def __init__(self, mounts: WorldMounts) -> None:
        self.mounts = mounts

    def __call__(self, spec: ToolSpec, args: dict[str, Any]) -> dict[str, Any] | None:
        if spec.level == 0:
            return None
        session = self.mounts.session(args["world"], args.get("speaker"))
        return Ladder(session).requires(spec.level)
