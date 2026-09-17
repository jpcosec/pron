"""The restaurant world and the servers over it that the spec 11 §8 and 12 tests talk to."""

from __future__ import annotations

import pytest
from pron.serve import Server
from pron.world.world import World
from remote.serving import running
from worlds.bare import init_bare
from worlds.restaurant import build_restaurant


@pytest.fixture(scope="module")
def world(tmp_path_factory) -> World:
    return build_restaurant(tmp_path_factory.mktemp("restaurant"))


@pytest.fixture(scope="module")
def server(world: World):
    with running(Server(world.root, world.store.pythonpath)) as srv:
        yield srv


@pytest.fixture(scope="module")
def restaurant(world: World) -> World:
    """The restaurant under the name a daemon of several worlds gives it."""
    return world


@pytest.fixture(scope="module")
def agent_world(tmp_path_factory) -> World:
    """A second, bare world: what an agent's own world looks like before it learns anything."""
    root = tmp_path_factory.mktemp("agent") / "world"
    init_bare(root)
    return World(root, str(root))


@pytest.fixture(scope="module")
def daemon(restaurant: World, agent_world: World, tmp_path_factory):
    sock = tmp_path_factory.mktemp("sock") / "pron.sock"
    worlds = [
        ("restaurant", restaurant.root, restaurant.store.pythonpath),
        ("agent", agent_world.root, agent_world.store.pythonpath),
    ]
    with running(Server(sock=sock, worlds=worlds), sock) as srv:
        yield srv
