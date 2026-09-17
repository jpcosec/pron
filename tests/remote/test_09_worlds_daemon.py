"""Several worlds in one daemon (spec 12 §6, §7): each client speaks to its own world; another
world opens only through the projections that world exposes, its interface lexicon, never
through its store; a world can be mounted on the running daemon."""

from __future__ import annotations

import pytest

from pron.remote import RemoteSession, alive, request, socket_path
from pron.serve import Server
from pron.world.world import World
from worlds.bare import init_bare

NOW = "2026-09-09"


def test_one_daemon_serves_two_worlds_and_each_world_socket_points_at_it(
    daemon: Server, restaurant: World, agent_world: World
):
    listing = request(daemon.path, {"op": "worlds"})
    assert (
        set(listing["worlds"]) == {"restaurant", "agent"}
        and listing["default"] == "restaurant"
    )
    assert (
        socket_path(restaurant.root).is_symlink()
        and socket_path(agent_world.root).is_symlink()
    )
    assert alive(
        socket_path(agent_world.root)
    )  # a client that only knows the world finds the daemon
    by_name = RemoteSession(daemon.path, world="restaurant", speaker="a", now=NOW)
    by_root = RemoteSession(
        socket_path(restaurant.root), world=str(restaurant.root), speaker="a", now=NOW
    )
    assert (
        "table 12" in by_name.turn("the large tables").text
        and "table 12" in by_root.turn("the large tables").text
    )
    assert request(daemon.path, {"op": "ping", "world": "agent"})["name"] == "agent"


def _to_restaurant(daemon: Server, home: str, speaker: str, projection: str = "all"):
    return RemoteSession(
        daemon.path,
        world="restaurant",
        home=home,
        projection=projection,
        speaker=speaker,
        now=NOW,
    )


def _expose_booking(restaurant: World) -> None:
    proj = dict(
        restaurant.projection("all"),
        name="booking",
        exposed=True,
        actions=["create"],
        relations=[
            {"name": "booked_by", "mode": "read and assert"},
            {"name": "assigned_to", "mode": "read and assert"},
            {"name": "transitions_to", "mode": "read"},
        ],
    )
    restaurant.store.create(
        "ProjectionDoc",
        "projection-booking",
        proj,
        restaurant.root / "knowledge" / "projections" / "booking.md",
    )


def _may_only_speak(interface: RemoteSession) -> None:
    with pytest.raises(RuntimeError, match="may only speak"):
        interface.payload("Table", "table-12")  # no access to the store, only sentences
    with pytest.raises(RuntimeError, match="may only speak"):
        interface.graph.nodes_of_type(node_type="Table")


def test_another_world_opens_only_an_exposed_projection(
    daemon: Server, restaurant: World
):
    with pytest.raises(RuntimeError, match="not exposed"):
        _to_restaurant(daemon, "agent", "agent.zero/run-1").turn("the large tables")
    _expose_booking(restaurant)
    interface = _to_restaurant(daemon, "agent", "agent.zero/run-1", "booking")
    assert any(
        r["form"].startswith("book") for r in interface.lexicon()
    )  # the interface lexicon: what the other world can say
    r = interface.turn("the large tables on the terrace")
    assert r.outcome == "unico" and "table 12" in r.text
    _may_only_speak(interface)
    own = _to_restaurant(daemon, "restaurant", "staff")
    assert (
        own.payload("Table", "table-12")["number"] == 12
    )  # the world's own client keeps everything


def test_mount_adds_a_world_to_the_running_daemon(daemon: Server, tmp_path):
    root = tmp_path / "third"
    init_bare(root)
    assert (
        request(
            daemon.path,
            {
                "op": "mount",
                "name": "third",
                "root": str(root),
                "pythonpath": str(root),
            },
        )["world"]
        == "third"
    )
    assert "third" in request(daemon.path, {"op": "worlds"})["worlds"] and alive(
        socket_path(root)
    )
