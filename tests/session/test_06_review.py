"""What the review of 2026-09-08 found missing against the spec: the correction after a missing
turn (06), pre-validation of a coordinated move (11 §7), undo refusing documents changed since
(11 §7), permissions inside a compose alias (05), the projection cutting the lexicon (01),
the second hash_mundo read before executing (11 §5), and the name of a created object
rendered once its relations exist."""

from __future__ import annotations

import re

import pytest

from pron.world.lexicon import Lexicon
from pron.session import Session
from pron.sexpr.prevalidation.prevalidator import Prevalidator
from pron.world.world import World
from worlds.restaurant import build_restaurant

NOW = "2026-09-09"
RES = "reservation-2026-09-11-ana-rojas"


@pytest.fixture(scope="module")
def world(tmp_path_factory) -> World:
    return build_restaurant(tmp_path_factory.mktemp("restaurant"))


@pytest.fixture(scope="module")
def session(world: World) -> Session:
    return Session(world, projection="all", speaker="jp", now=NOW)


def test_a_fragment_that_fits_the_hole_corrects_the_missing_turn(session: Session):
    assert (
        session.turn("create a client named Ana Rojas, phone 9 5555 1234").outcome
        == "unico"
    )
    r = session.turn("book her a table on the patio for 6 people on Friday at 9pm")
    assert r.outcome == "missing" and "patio" in r.text
    missing_move = r.move_id
    r = session.turn("on the terrace")
    assert r.outcome == "unico", r.text + " / " + " | ".join(r.trace)
    assert (
        r.record["corrects"]["move"] == missing_move
        and "terrace" in r.record["corrects"]["sentence"]
    )
    assert session.world.store.doc("Reservation", RES) is not None
    move = session.ledger.get(r.move_id)
    assert move["refers_to"] == missing_move


def test_the_created_object_is_named_once_its_relations_exist(session: Session):
    r = session.turn("the reservation")
    assert re.search(r"table \d+", r.text) and "table ," not in r.text


def test_a_coordinated_move_is_validated_whole_before_the_first_write(session: Session):
    before = session.world.store.payload("Reservation", RES)
    r = session.turn("change it to 100 people and confirm it")
    assert r.outcome == "error" and "party_size <= 8" in r.text, r.text
    after = session.world.store.payload("Reservation", RES)
    assert (
        after["party_size"] == before["party_size"] == 6
        and after["status"] == "pending"
    )
    assert r.record["writes"] == []
    assert any("dry run" in line for line in r.trace), r.trace


def test_undo_does_not_touch_a_document_changed_since_the_move(session: Session):
    r = session.turn("change it to 5 people")
    assert r.outcome == "unico", r.text
    session.world.store.update_field(
        "Reservation", RES, "party_size", 7
    )  # someone else, outside pron
    r = session.turn("undo the last move")
    assert r.outcome == "unico" and "Not touched" in r.text, r.text
    assert session.world.store.payload("Reservation", RES)["party_size"] == 7


def test_a_compose_alias_respects_the_relation_permissions(world: World):
    proj = dict(
        world.projection("all"),
        name="creator",
        actions=["create"],
        relations=[
            {"name": "booked_by", "mode": "read"},
            {"name": "assigned_to", "mode": "read"},
            {"name": "transitions_to", "mode": "read"},
        ],
    )
    world.store.create(
        "ProjectionDoc",
        "projection-creator",
        proj,
        world.root / "knowledge" / "projections" / "creator.md",
    )
    s = Session(world, projection="creator", speaker="zoe", now=NOW)
    assert s.turn("the client Luis Soto").outcome == "unico"
    r = s.turn("book him a table on the terrace for 2 people on Saturday at 8pm")
    assert r.outcome == "missing" and "not assert" in r.text, r.text
    assert world.store.doc("Reservation", "reservation-2026-09-12-luis-soto") is None


def test_the_projection_cuts_aliases_whose_target_is_outside_it(world: World):
    proj = dict(
        world.projection("all"),
        name="clients",
        models=["Client"],
        relations=[],
        actions=[],
    )
    world.store.create(
        "ProjectionDoc",
        "projection-clients",
        proj,
        world.root / "knowledge" / "projections" / "clients.md",
    )
    s = Session(world, projection="clients", now=NOW)
    r = s.turn("the tables")
    assert r.outcome == "missing" and "don't have" in r.text, r.text
    assert s.turn("the clients").outcome == "unico"


def test_hash_mundo_is_read_again_before_executing(world: World, monkeypatch):
    s = Session(world, projection="all", speaker="jp", now=NOW)
    original = Prevalidator.__call__
    calls = []

    def racing(self, parts, plans, ctx):
        if not calls:  # the first time through: the world changes between understanding and executing
            calls.append(1)
            s.world.store.create(
                "Table",
                "table-99",
                {"number": 99, "capacity": 2, "zone": "indoor"},
                s.world.root / "tables" / "99.md",
            )
        return original(self, parts, plans, ctx)

    monkeypatch.setattr(Prevalidator, "__call__", racing)
    r = s.turn("the large tables")
    assert r.outcome == "unico", r.text
    assert any("changed while understanding" in line for line in r.trace), r.trace


def test_a_model_identifier_is_also_known_split_into_words(world: World):
    lex = Lexicon(
        world,
        {"models": ["RelationTypeDoc"], "relations": [], "actions": [], "aliases": []},
    )
    assert [w.ref for w in lex.lookup("relation type doc")] == [
        "(model RelationTypeDoc)"
    ]


def test_a_complement_names_a_related_document_and_crosses_its_edges(world: World):
    s = Session(world, projection="all", speaker="jp", now=NOW)
    r = s.turn("the reservations of Luis Soto")
    assert r.outcome == "unico" and "20:00" in r.text, (
        r.text + " / " + " | ".join(r.trace)
    )
    assert any("booked_by" in q for q in r.trace), r.trace
    r = s.turn("Luis Soto's reservations for Friday")
    assert (
        r.outcome == "unico"
        and "20:00" in r.text
        and any('date = "2026-09-11"' in q for q in r.trace)
    ), r.text + " / " + " | ".join(r.trace)
    r = s.turn("Luis Soto's reservations for Saturday")
    assert r.outcome == "unico" and r.text == "None.", r.text
    r = s.turn("the tables of the reservations of Luis Soto")
    assert r.outcome == "unico" and r.text == "table 3.", (
        r.text + " / " + " | ".join(r.trace)
    )
    r = s.turn("confirm the reservation of Luis Soto")
    assert r.outcome == "unico" and "Done" in r.text, (
        r.text + " / " + " | ".join(r.trace)
    )
    assert (
        world.store.payload("Reservation", "reservation-2026-09-11-luis-soto")["status"]
        == "confirmed"
    )
    r = s.turn("the reservations of Nadie Nunca")
    assert r.outcome == "unico" and r.text == "None.", r.text


def test_a_read_only_session_writes_nothing_whatever_the_projection_allows(
    world: World,
):
    s = Session(world, projection="all", speaker="viewer", now=NOW, read_only=True)
    assert s.turn("the clients").outcome == "unico"
    r = s.turn("create a client named Zoe Lee, phone 1")
    assert (
        r.outcome == "missing" and world.store.doc("Client", "client-zoe-lee") is None
    ), r.text
    r = s.turn("confirm the reservation of Luis Soto")
    assert r.outcome == "missing", r.text
    assert all(
        not m["record"].get("writes")
        for m in (s.ledger.get(mid) for mid in [r.move_id])
    )


def test_removing_a_required_field_is_refused_not_raised(world: World):
    """A write whose payload would not validate is refused before anything is written
    (spec 11 §7), even when the model rejects it outright for a missing required field."""
    s = Session(world, projection="all", speaker="jp", now=NOW)
    assert s.turn("the tables on the terrace").outcome == "unico"
    r = s.turn("remove the zone of them")
    assert r.outcome == "error" and "zone" in r.text and "round-trip" in r.text
    assert not r.record["writes"]
    assert s.turn("the tables on the terrace").outcome == "unico"
