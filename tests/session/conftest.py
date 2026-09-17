"""The restaurant world of the spec 09 conversation, and the session that holds it."""

from __future__ import annotations

import pytest

from pron.session import Session
from pron.world.world import World
from worlds.restaurant import build_restaurant


@pytest.fixture(scope="module")
def world(tmp_path_factory) -> World:
    return build_restaurant(tmp_path_factory.mktemp("restaurant"))


@pytest.fixture(scope="module")
def session(world: World) -> Session:
    return Session(world, projection="all", speaker="jp", now="2026-09-09")
