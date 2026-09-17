"""The restaurant world whose documents the corpus tests index."""

from __future__ import annotations

import pytest

from pron.world.world import World
from worlds.restaurant import build_restaurant


@pytest.fixture(scope="module")
def world(tmp_path_factory) -> World:
    return build_restaurant(tmp_path_factory.mktemp("restaurant"))
