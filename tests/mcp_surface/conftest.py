"""The restaurant world mounted by an MCP app (spec 14): the read tests share one, read-only."""

from __future__ import annotations

import pytest

from mcp_surface.mounted import mount
from pron.mcp.app import McpApp
from pron.world.world import World
from worlds.restaurant import build_restaurant


@pytest.fixture(scope="module")
def world(tmp_path_factory) -> World:
    return build_restaurant(tmp_path_factory.mktemp("restaurant"))


@pytest.fixture(scope="module")
def app(world: World) -> McpApp:
    return mount(world)


@pytest.fixture(scope="module")
def get(app: McpApp):
    """kb_get through the tool table, as the server runs it."""
    return lambda uri: app.tools.call("kb_get", uri=uri)
