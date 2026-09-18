"""What one `pron mcp` serves (spec 14 §1): the mounted worlds and their sessions, the read
plane, the tool table and the audit hook. The composition root: registering a family of
tools is one line in `McpApp.open`, and the SDK server is built from the table.
"""

from __future__ import annotations

from dataclasses import dataclass

from pron.mcp.audit_tool import AuditTool
from pron.mcp.ladder_gate import LadderGate
from pron.mcp.model_tools import ModelTools
from pron.mcp.read_plane import ReadPlane
from pron.mcp.read_tools import ReadTools
from pron.mcp.tool_table import ToolTable
from pron.mcp.world_mounts import WorldMounts
from pron.mcp.write_tools import WriteTools


@dataclass
class McpApp:
    """The server's state, independent of the MCP SDK."""

    mounts: WorldMounts
    plane: ReadPlane
    tools: ToolTable
    audit: str | None = None

    @staticmethod
    def open(
        worlds: list[str],
        pythonpath: str | None = None,
        projection: str = "all",
        speaker: str = "mcp",
        audit: str | None = None,
    ) -> "McpApp":
        """Mount the worlds (writing nothing), fill the tool table and put the ladder of
        mutability at its door (spec 14 §5)."""
        mounts = WorldMounts(worlds, pythonpath, projection, speaker)
        app = McpApp(mounts, ReadPlane(mounts), ToolTable(LadderGate(mounts)), audit)
        ReadTools(app.plane).register(app.tools)
        AuditTool(app).register(app.tools)
        WriteTools(app).register(app.tools)
        ModelTools(app).register(app.tools)
        return app
