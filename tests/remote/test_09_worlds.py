"""Several worlds in one daemon (spec 12 §6, §7): each client speaks to its own world; another
world opens only through the projections that world exposes, its interface lexicon, never
through its store; a template gives a new world its words; a turn records what it read."""

from __future__ import annotations

import threading
import time
from pathlib import Path

import pytest
from sldb.runtime.validation import render_model_markdown

from pron.remote import RemoteSession, alive, request, socket_path
from pron.serve import Server
from pron.session import Session
from pron.world.world import World, apply_template, init_world
from worlds.restaurant import build_restaurant

NOW = "2026-09-09"


@pytest.fixture(scope="module")
def restaurant(tmp_path_factory) -> World:
    return build_restaurant(tmp_path_factory.mktemp("restaurant"))


@pytest.fixture(scope="module")
def agent_world(tmp_path_factory) -> World:
    """A second, bare world: what an agent's own world looks like before it learns anything."""
    root = tmp_path_factory.mktemp("agent") / "world"
    root.mkdir()
    from sldb.cli import main as sldb_main

    assert sldb_main(["stores", "init", "--path", str(root)]) == 0
    init_world(root, str(root))
    return World(root, str(root))


@pytest.fixture(scope="module")
def daemon(restaurant: World, agent_world: World, tmp_path_factory):
    sock = tmp_path_factory.mktemp("sock") / "pron.sock"
    srv = Server(
        sock=sock,
        worlds=[
            ("restaurant", restaurant.root, restaurant.store.pythonpath),
            ("agent", agent_world.root, agent_world.store.pythonpath),
        ],
    )
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    for _ in range(100):
        if alive(sock):
            break
        time.sleep(0.05)
    assert alive(sock)
    yield srv
    request(sock, {"op": "stop"})
    t.join(timeout=10)


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


def test_another_world_opens_only_an_exposed_projection(
    daemon: Server, restaurant: World
):
    foreign = RemoteSession(
        daemon.path,
        world="restaurant",
        home="agent",
        projection="all",
        speaker="agent.zero/run-1",
        now=NOW,
    )
    with pytest.raises(RuntimeError, match="not exposed"):
        foreign.turn("the large tables")
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
    interface = RemoteSession(
        daemon.path,
        world="restaurant",
        home="agent",
        projection="booking",
        speaker="agent.zero/run-1",
        now=NOW,
    )
    assert any(
        r["form"].startswith("book") for r in interface.lexicon()
    )  # the interface lexicon: what the other world can say
    r = interface.turn("the large tables on the terrace")
    assert r.outcome == "unico" and "table 12" in r.text
    with pytest.raises(RuntimeError, match="may only speak"):
        interface.payload("Table", "table-12")  # no access to the store, only sentences
    with pytest.raises(RuntimeError, match="may only speak"):
        interface.graph.nodes_of_type(node_type="Table")
    own = RemoteSession(
        daemon.path,
        world="restaurant",
        home="restaurant",
        projection="all",
        speaker="staff",
        now=NOW,
    )
    assert (
        own.payload("Table", "table-12")["number"] == 12
    )  # the world's own client keeps everything


def test_mount_adds_a_world_to_the_running_daemon(daemon: Server, tmp_path):
    root = tmp_path / "third"
    root.mkdir()
    from sldb.cli import main as sldb_main

    assert sldb_main(["stores", "init", "--path", str(root)]) == 0
    init_world(root, str(root))
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


def _template(tmp_path: Path) -> Path:
    """A world template: one alias and one exposed projection, rendered from their models."""
    from pron.models.anchor import AnchorDoc
    from pron.models.projection import ProjectionDoc

    t = tmp_path / "template"
    (t / "anchors").mkdir(parents=True, exist_ok=True)
    (t / "projections").mkdir(parents=True, exist_ok=True)
    (t / "anchors" / "move.md").write_text(
        render_model_markdown(
            AnchorDoc,
            {
                "symbol": "move",
                "forms": ["move", "moves"],
                "ref": "model:MoveDoc",
                "steps": [],
                "motive": "a recorded turn",
            },
        )
        + "\n",
        encoding="utf-8",
    )
    (t / "projections" / "interface.md").write_text(
        render_model_markdown(
            ProjectionDoc,
            {
                "name": "interface",
                "stores": ["local"],
                "models": ["MoveDoc"],
                "relations": [],
                "actions": [],
                "aliases": ["all"],
                "naming": {},
                "display": {},
                "key": {},
                "matching": {"neighbors": 3, "threshold": 0.55},
                "exposed": True,
                "description": "what other worlds may ask",
            },
        )
        + "\n",
        encoding="utf-8",
    )
    return t


def test_a_template_gives_a_new_world_its_words(tmp_path):
    root = tmp_path / "born"
    root.mkdir()
    from sldb.cli import main as sldb_main

    assert sldb_main(["stores", "init", "--path", str(root)]) == 0
    report = init_world(root, str(root), template=_template(tmp_path))
    assert set(report["template_added"]) == {
        "AnchorDoc:anchor-move",
        "ProjectionDoc:projection-interface",
    }
    world = World(root, str(root))
    assert world.projection("interface")["exposed"] is True
    s = Session(world, projection="interface", now=NOW)
    assert s.turn("the moves").outcome == "unico"
    assert apply_template(root, _template(tmp_path), str(root)) == []  # idempotent


def test_a_turn_records_what_it_read_with_its_hash(restaurant: World):
    s = Session(restaurant, projection="all", speaker="jp", now=NOW)
    r = s.turn("the reservations of Luis Soto")
    reads = {x["address"]: x["hash_c"] for x in r.record["reads"]}
    assert (
        "Client:client-luis-soto" in reads
        and "Reservation:reservation-2026-09-11-luis-soto" in reads
    )
    assert all(len(h) == 64 for h in reads.values())
    assert reads["Client:client-luis-soto"] == restaurant.store.hash_c(
        "Client", "client-luis-soto"
    )
    move = s.ledger.get(r.move_id)
    assert move["record"]["reads"] == r.record["reads"]
