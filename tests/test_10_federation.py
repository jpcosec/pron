"""One store linking the nodes' stores (spec 01 §Un mundo en varios stores): a session whose
home is a linked store resolves, writes and records there; an orchestrator's projection over
several stores reads them all; nothing is copied."""

from __future__ import annotations

import pytest

from pron.kernel.ids import address_of, split_id
from pron.session import Session
from pron.world.world import World, init_world
from worlds.restaurant import build_restaurant

NOW = "2026-09-09"


@pytest.fixture(scope="module")
def nodes(tmp_path_factory):
    a = build_restaurant(tmp_path_factory.mktemp("a"))
    b = build_restaurant(tmp_path_factory.mktemp("b"))
    return a, b


@pytest.fixture(scope="module")
def daemon(nodes, tmp_path_factory) -> World:
    """The daemon's own store, empty of restaurant documents, linking A and B."""
    a, b = nodes
    root = tmp_path_factory.mktemp("daemon") / "world"
    root.mkdir()
    from sldb.cli import main as sldb_main

    assert sldb_main(["stores", "init", "--path", str(root)]) == 0
    init_world(root, str(root))
    d = World(root, str(root))
    assert d.store.link("A", a.root) and d.store.link("B", b.root)
    assert not d.store.link("A", a.root)
    proj = dict(
        d.projection("all"),
        name="orq",
        stores=["local", "A", "B"],
        models=["Reservation", "Client", "Table"],
        actions=[],
        relations=[
            {"name": "booked_by", "mode": "read"},
            {"name": "assigned_to", "mode": "read"},
        ],
    )
    d.store.create(
        "ProjectionDoc",
        "projection-orq",
        proj,
        root / "knowledge" / "projections" / "orq.md",
    )
    return d


def test_a_session_at_home_in_a_linked_store_lives_there(daemon: World, nodes):
    a, _ = nodes
    s = Session(daemon, projection="all", speaker="node-a", now=NOW, home="A")
    r = s.turn("the large tables")
    assert r.outcome == "unico" and "table 12" in r.text, (
        r.text + " / " + " | ".join(r.trace)
    )
    assert any("A:st.{Table+}" in q for q in r.trace)  # the scope names the store
    assert all(split_id(x["address"])[0] == "A" for x in r.record["reads"])
    assert daemon.store.doc("MoveDoc", r.move_id, "A") is not None  # the ledger is A's
    assert daemon.store.doc("MoveDoc", r.move_id) is None
    r = s.turn("create a client named Ana Rojas, phone 9 5555 1234")
    assert r.outcome == "unico", r.text
    assert a.store.doc("Client", "client-ana-rojas") is not None  # written in A's store
    assert daemon.store.doc("Client", "client-ana-rojas") is None
    r = s.turn("book her a table on the terrace for 6 people on Friday at 9pm")
    assert r.outcome == "unico" and "table 12" in r.text, (
        r.text + " / " + " | ".join(r.trace)
    )
    assert (
        a.store.doc(
            "RelationDoc",
            "booked_by--Reservation:reservation-2026-09-11-ana-rojas--Client:client-ana-rojas",
        )
        is not None
    )  # written as A reads itself
    r = s.turn("the reservations of Ana Rojas")
    assert r.outcome == "unico" and "table 12" in r.text, (
        r.text + " / " + " | ".join(r.trace)
    )
    r = s.turn("confirm it")
    assert (
        r.outcome == "unico"
        and a.store.payload("Reservation", "reservation-2026-09-11-ana-rojas")["status"]
        == "confirmed"
    )


def test_an_orchestrator_projection_reads_every_store_it_names(daemon: World, nodes):
    s = Session(daemon, projection="orq", speaker="orq", now=NOW)
    r = s.turn("the reservations")
    assert r.outcome == "unico" and r.text.startswith("3:"), (
        r.text + " / " + " | ".join(r.trace)
    )  # Luis in A, Luis in B, Ana in A
    stores = {split_id(x["address"])[0] for x in r.record["reads"]}
    assert stores == {"A", "B"}
    r = s.turn("the reservations of Luis Soto")
    assert r.outcome == "unico" and r.text.startswith("2:"), r.text
    assert (
        s.turn("create a client named Zoe Lee, phone 1").outcome == "missing"
    )  # no actions in orq


def test_a_world_alone_still_works_the_same(nodes):
    a, _ = nodes
    s = Session(a, projection="all", speaker="alone", now=NOW)
    r = s.turn("the reservations of Ana Rojas")
    assert r.outcome == "unico" and "confirmed" in r.text, r.text
    assert (
        address_of("Reservation:x") == "st.{Reservation}.x"
        and address_of("A:Reservation:x") == "A:st.{Reservation}.x"
    )
