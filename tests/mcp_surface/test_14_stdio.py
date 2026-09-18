"""spec 14 §1: `pron mcp` over the real transport — a subprocess on stdio, driven by the MCP
SDK's own client, over a copy of the restaurant world."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import anyio
import pytest

import pron

stdio = pytest.importorskip("mcp.client.stdio")
from mcp import ClientSession  # noqa: E402


def server(world) -> stdio.StdioServerParameters:
    src = str(Path(pron.__file__).parents[1])
    args = ["-m", "pron.cli.main", "mcp", "--world", f"rest={world.root}"]
    env = {**os.environ, "PYTHONPATH": src}
    return stdio.StdioServerParameters(
        command=sys.executable,
        args=[*args, "--pythonpath", world.store.pythonpath],
        env=env,
    )


async def talk(world) -> dict:
    """worlds_list and kb_get as tools, and one resource read, in one session."""
    async with stdio.stdio_client(server(world)) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            listed = await session.call_tool("worlds_list", {})
            got = await session.call_tool("kb_get", {"uri": "kb://rest/Table/table-3"})
            resource = await session.read_resource("kb://rest/Table/@terrace")
    return {
        "tools": [t.name for t in tools.tools],
        "worlds": json.loads(listed.content[0].text),
        "table": json.loads(got.content[0].text),
        "terrace": json.loads(resource.contents[0].text),
    }


def test_pron_mcp_answers_over_stdio(world):
    out = anyio.run(talk, world)
    assert out["tools"] == [
        "worlds_list",
        "kb_get",
        "kb_find",
        "kb_read",
        "kb_neighbors",
    ]
    assert out["worlds"]["worlds"][0]["name"] == "rest"
    assert out["table"]["payload"] == {"number": 3, "capacity": 4, "zone": "indoor"}
    assert [d["id"] for d in out["terrace"]["documents"]] == [
        "Table:table-12",
        "Table:table-14",
        "Table:table-20",
    ]
