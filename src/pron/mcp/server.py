"""The MCP server itself (spec 14 §1): the SDK's server over stdio, filled from an `McpApp` —
every tool of its table, and one resource template for every `kb://` address (spec 14 §2).
The only module of pron that imports the MCP SDK.

The SDK is `mcp` 2.x, where FastMCP is called `MCPServer`. A resource URI cannot carry a
bare `?` in its path, so the ranked search as a resource is `kb://{world}/%3F{text}`;
`kb_get` takes `kb://{world}/?{text}` as written.
"""

from __future__ import annotations

import json

from mcp.server.mcpserver import MCPServer

from pron.mcp.app import McpApp

INSTRUCTIONS = (
    "pron: sldb worlds as documents and typed edges. Read with kb_get and kb:// addresses; "
    "every document comes with its literal address. No tool takes a sentence."
)


def build(app: McpApp) -> MCPServer:
    """An SDK server with the app's tools and the `kb://` resource template."""
    server = MCPServer("pron", instructions=INSTRUCTIONS)
    for spec in app.tools:
        server.add_tool(
            app.tools.guarded(spec), name=spec.name, description=spec.description
        )

    @server.resource("kb://{world}/{+path}", mime_type="application/json")
    def kb(world: str, path: str) -> str:
        """Any kb:// address of spec 14 §2."""
        answer = app.plane.get(f"kb://{world}/{path}")
        return json.dumps(answer, ensure_ascii=False, default=str)

    return server


def run(app: McpApp) -> None:
    """Serve over stdio until the client closes it."""
    build(app).run("stdio")
