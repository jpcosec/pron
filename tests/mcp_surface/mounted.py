"""Helpers of the MCP surface tests (spec 14): an app over a world, and a set's ids."""

from __future__ import annotations

from pron.mcp.app import McpApp
from pron.world.world import World


def mount(world: World, name: str = "rest") -> McpApp:
    return McpApp.open([f"{name}={world.root}"], world.store.pythonpath)


def ids(answer: dict) -> list[str]:
    return [d["id"] for d in answer["documents"]]
