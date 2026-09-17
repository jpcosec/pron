"""Moves whose (doc …) refer to what the same move creates (spec 06 §Coordinación, 13).
A pending create is resolvable by its (as …) name inside its own move; execution writes
the creates before the parts that reference them; a name nothing creates is still missing."""

from __future__ import annotations

import pytest

from pron.session import Session
from pron.world.world import World
from worlds.restaurant import build_restaurant

NOW = "2026-09-09"


@pytest.fixture(scope="module")
def world(tmp_path_factory) -> World:
    return build_restaurant(tmp_path_factory.mktemp("pending"))


def session(world: World, **kw) -> Session:
    return Session(world, projection="all", speaker="runtime", now=NOW, **kw)


def test_move_asserts_between_two_creates(world: World):
    s = session(world)
    r = s.eval(
        '(move (create Client (as "x1") (name "Nueva Una") (phone "111"))'
        ' (create Reservation (as "x2") (date "2026-09-10") (time "21:00") (party_size 3))'
        ' (assert booked_by (doc "Reservation:x2") (doc "Client:x1")))'
    )
    assert r.outcome == "unico", r.text + " | " + " | ".join(r.trace)
    assert world.store.payload_of("Client:x1")["name"] == "Nueva Una"
    assert world.store.payload_of("Reservation:x2")["party_size"] == 3
    edges = [
        e
        for e in s.verbs.edges_from("Reservation:x2").edges
        if e["relation"] == "booked_by"
    ]
    assert edges and edges[0]["target"] == "Client:x1"
    move = world.store.payload("MoveDoc", r.move_id)
    assert any(w["verb"] == "create" for w in move["record"]["writes"])


def test_forward_reference_create_after_the_assert(world: World):
    s = session(world)
    r = s.eval(
        '(move (assert booked_by (doc "Reservation:x4") (doc "Client:x4c"))'
        ' (create Client (as "x4c") (name "Nueva Cuatro") (phone "444"))'
        ' (create Reservation (as "x4") (date "2026-09-10") (time "22:00") (party_size 2)))'
    )
    assert r.outcome == "unico", r.text + " | " + " | ".join(r.trace)
    edges = [
        e
        for e in s.verbs.edges_from("Reservation:x4").edges
        if e["relation"] == "booked_by"
    ]
    assert edges and edges[0]["target"] == "Client:x4c"


def test_a_name_nobody_creates_is_still_missing(world: World):
    s = session(world)
    r = s.eval(
        '(move (create Client (as "x3") (name "Nueva Tres") (phone "333"))'
        ' (assert booked_by (doc "Reservation:never") (doc "Client:x3")))'
    )
    assert r.outcome == "missing", r.text
    assert world.store.doc("Client", "x3") is None
    assert world.store.doc("Reservation", "never") is None


def test_undo_of_a_move_with_creates_and_assert(world: World):
    s = session(world)
    r = s.eval(
        '(move (create Client (as "x5") (name "Nueva Cinco") (phone "555"))'
        ' (create Reservation (as "x6") (date "2026-09-11") (time "20:00") (party_size 2))'
        ' (assert booked_by (doc "Reservation:x6") (doc "Client:x5")))'
    )
    assert r.outcome == "unico", r.text + " | " + " | ".join(r.trace)
    u = s.eval("(undo)")
    assert u.outcome == "unico", u.text
    assert world.store.doc("Client", "x5") is None
    assert world.store.doc("Reservation", "x6") is None
    edges = [
        e
        for e in s.verbs.edges_from("Reservation:x6").edges
        if e["relation"] == "booked_by"
    ]
    assert not edges
