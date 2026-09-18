"""Steps 4–7 through the conversation of spec 09: creation, a compose alias, missing and its
correction, ambiguity and its answer, a transition with a condition, coordinated writes,
condition re-evaluation, why, undo. Every turn leaves a MoveDoc. The turns follow each other
in this file."""

from __future__ import annotations

from pron.session import Session
from pron.world.doc_id import DocId
from pron.world.world import World

NOW = "2026-09-09"
RES = "reservation-2026-09-11-ana-rojas"


def _said(r) -> str:
    return _said(r)


def test_turn_1_create_with_payload(session: Session):
    r = session.turn("create a client named Ana Rojas, phone 9 5555 1234")
    assert r.outcome == "unico", r.text
    assert "Ana Rojas" in r.text
    assert (
        session.world.store.get("st.{Client}.client-ana-rojas.phone") == "9 5555 1234"
    )
    assert r.record["writes"][0]["verb"] == "create"
    assert session.world.store.doc(DocId.of("MoveDoc", r.move_id)) is not None


def test_turn_2_unknown_enum_value_is_missing_before_any_query(session: Session):
    r = session.turn("book her a table on the patio for 6 people on Friday at 9pm")
    assert r.outcome == "missing"
    assert "patio" in r.text and "terrace" in r.text
    assert r.record["queries"] == []


def test_turn_3_compose_creates_the_reservation_and_two_relations(session: Session):
    r = session.turn("book her a table on the terrace for 6 people on Friday at 9pm")
    assert r.outcome == "unico", _said(r)
    res = session.world.store.doc(DocId.of("Reservation", RES))
    assert (
        res is not None
        and res.payload["party_size"] == 6
        and res.payload["time"] == "21:00"
        and res.payload["status"] == "pending"
    )
    edges = {
        e["relation"]: e["target"]
        for e in session.verbs.edges_from(f"Reservation:{RES}").edges
        if e["relation"] in ("booked_by", "assigned_to")
    }
    assert edges == {
        "booked_by": "Client:client-ana-rojas",
        "assigned_to": "Table:table-12",
    }
    assert "table 12" in r.text and "14" in r.text
    assert session.world.graph_is_fresh()


def test_turn_4_and_5_ambiguity_then_answer(session: Session):
    r = session.turn("what reservations does Ana have for Friday?")
    assert r.outcome == "ambiguo" and "Ana Pérez" in r.text and "Ana Rojas" in r.text
    assert session.dialogue.state == "pendiente"
    r = session.turn("Rojas")
    assert r.outcome == "unico", _said(r)
    assert "2026-09-11" in r.text and "6 people" in r.text and "table 12" in r.text
    assert session.dialogue.state == "libre"


def test_turn_6_confirm_is_a_guarded_transition(session: Session):
    r = session.turn("confirm it")
    assert r.outcome == "unico", _said(r)
    assert session.world.store.get(f"st.{{Reservation}}.{RES}.status") == "confirmed"
    assert any("legal" in line for line in r.trace)


def test_turn_7_two_writes_and_a_condition_that_breaks(session: Session):
    r = session.turn("change it to 9 people and add a note saying: birthday")
    assert r.outcome == "unico", _said(r)
    p = session.world.store.payload(DocId.of("Reservation", RES))
    assert p["party_size"] == 9 and p["notes"] == "birthday"
    assert "Heads up" in r.text and "capacity >= {party_size}" in r.text
    assert len(r.record["writes"]) == 2


def test_turn_8_why_reads_the_ledger(session: Session):
    r = session.turn("why?")
    assert r.outcome == "unico"
    assert "9 people" in r.text or "party_size" in r.text


def test_illegal_transition_is_refused(session: Session):
    r = session.turn("seat them")
    # 'them' is plural: the last set is the one reservation; seating a confirmed reservation is legal
    assert r.outcome in ("unico", "error"), r.text
    r = session.turn("confirm it")
    assert r.outcome == "error" and "transition" in r.text or "cannot" in r.text


def test_undo_restores_the_previous_values(session: Session):
    before = session.world.store.payload(DocId.of("Reservation", RES))["party_size"]
    r = session.turn("change it to 4 people")
    assert r.outcome == "unico", r.text
    r = session.turn("undo the last move")
    assert r.outcome == "unico", _said(r)
    assert (
        session.world.store.payload(DocId.of("Reservation", RES))["party_size"]
        == before
    )


def test_read_only_projection_cannot_write(world: World):
    proj = dict(
        world.projection("all"),
        actions=[],
        relations=[{"name": "booked_by", "mode": "read"}],
    )
    world.store.create(
        DocId.of("ProjectionDoc", "projection-reader"),
        dict(proj, name="reader"),
        world.root / "knowledge" / "projections" / "reader.md",
    )
    s = Session(world, projection="reader", now=NOW)
    r = s.turn("the large tables")
    assert r.outcome == "unico" and "table 12" in r.text
    r = s.turn("create a client named Zoe Lee, phone 1")
    assert r.outcome == "missing"


def test_every_turn_left_a_move(world: World):
    moves = world.store.docs_of("MoveDoc")
    assert len(moves) >= 12
    assert all(m.payload["hash_before"] for m in moves)
