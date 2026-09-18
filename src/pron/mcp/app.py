"""What one `pron mcp` serves (spec 14 §1): the mounted worlds and their sessions, the read
plane, the tool table and the audit hook. The composition root: registering a family of
tools is one line in `McpApp.open`, and the SDK server is built from the table.
"""

from __future__ import annotations

from dataclasses import dataclass

from pron.mcp.read_plane import ReadPlane
from pron.mcp.read_tools import ReadTools
from pron.mcp.tool_table import ToolTable
from pron.mcp.world_mounts import WorldMounts


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
        """Mount the worlds (writing nothing) and fill the tool table."""
        mounts = WorldMounts(worlds, pythonpath, projection, speaker)
        app = McpApp(mounts, ReadPlane(mounts), ToolTable(), audit)
        ReadTools(app.plane).register(app.tools)
        return app
