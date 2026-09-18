"""Undo and the dialogue (spec 06, 11 §7): what an undo took out of the store is no longer an
antecedent, and saying "undo the last move" again goes one move further back."""

from __future__ import annotations

from pron.session import Session
from worlds.restaurant import build_restaurant

from pron.world.doc_id import DocId

NOW = "2026-09-09"
ANA = "reservation-2026-09-11-ana-rojas"


def _booked(tmp_path) -> Session:
    session = Session(build_restaurant(tmp_path), speaker="jp", now=NOW)
    session.turn("create a client named Ana Rojas, phone 9 5555 1234")
    session.turn("book her a table on the terrace for 6 people on Friday at 9pm")
    return session


def test_an_undone_create_is_no_longer_it(tmp_path):
    session = _booked(tmp_path)
    session.turn("undo the last move")
    r = session.turn("confirm it")
    assert ANA not in r.text, r.text
    assert all(ANA not in a for a in session.dialogue.singular.values())


def test_undo_again_takes_back_the_move_before(tmp_path):
    session = _booked(tmp_path)
    first = session.turn("undo the last move")
    r = session.turn("undo the last move")
    assert "(1 write(s))" in r.text, r.text
    assert r.record["undoes"] != first.record["undoes"]
    assert session.world.store.doc(DocId.of("Client", "client-ana-rojas")) is None
    assert session.world.store.doc(DocId.of("Reservation", ANA)) is None


def test_nothing_left_to_undo(tmp_path):
    session = Session(build_restaurant(tmp_path), speaker="jp", now=NOW)
    session.turn("create a client named Eva Diaz, phone 9 4444 0000")
    session.turn("undo the last move")
    assert session.turn("undo the last move").text == "Nothing to undo."
