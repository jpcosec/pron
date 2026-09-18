"""What the review of 2026-09-08 found missing against the spec, along one conversation: the
correction after a missing turn (06), the name of a created object rendered once its relations
exist, pre-validation of a coordinated move (11 §7), and undo refusing documents changed
since (11 §7). The tests follow each other in this file."""

from __future__ import annotations

import re


from pron.session import Session
from pron.world.doc_id import DocId

NOW = "2026-09-09"
RES = "reservation-2026-09-11-ana-rojas"


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
    assert session.world.store.doc(DocId.of("Reservation", RES)) is not None
    move = session.ledger.get(r.move_id)
    assert move["refers_to"] == missing_move


def test_the_created_object_is_named_once_its_relations_exist(session: Session):
    r = session.turn("the reservation")
    assert re.search(r"table \d+", r.text) and "table ," not in r.text


def test_a_coordinated_move_is_validated_whole_before_the_first_write(session: Session):
    before = session.world.store.payload(DocId.of("Reservation", RES))
    r = session.turn("change it to 100 people and confirm it")
    assert r.outcome == "error" and "party_size <= 8" in r.text, r.text
    after = session.world.store.payload(DocId.of("Reservation", RES))
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
        DocId.of("Reservation", RES), "party_size", 7
    )  # someone else, outside pron
    r = session.turn("undo the last move")
    assert r.outcome == "unico" and "Not touched" in r.text, r.text
    assert session.world.store.payload(DocId.of("Reservation", RES))["party_size"] == 7
