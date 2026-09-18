"""Referents the dialogue keeps (spec 06): the candidate an answer picks is the singular
antecedent of its class."""

from __future__ import annotations

from pron.session import Session
from worlds.restaurant import build_restaurant

from pron.world.doc_id import DocId

NOW = "2026-09-09"


def test_the_picked_candidate_is_the_singular_referent(tmp_path):
    session = Session(build_restaurant(tmp_path), speaker="jp", now=NOW)
    session.turn("create a client named Ana Rojas, phone 9 5555 1234")
    asked = session.turn("what reservations does Ana have?")
    assert asked.outcome == "ambiguo", asked.text
    chosen = session.dialogue.pending.candidates[0]
    session.turn("1")
    assert session.dialogue.singular["Client"] == chosen


def test_a_field_of_several_classes_takes_the_class_of_the_antecedent(tmp_path):
    """'notes' is a field of Client and of Reservation: 'it' is whichever the dialogue left."""
    session = Session(build_restaurant(tmp_path), speaker="jp", now=NOW)
    luis = "Reservation:reservation-2026-09-11-luis-soto"
    assert session.eval(f'(change (doc "{luis}") notes "window")').outcome == "unico"
    r = session.turn("remove the notes of it")
    assert r.outcome == "unico", r.text
    assert r.record["writes"][0]["address"] == luis
    assert session.world.store.payload(DocId.parse(luis)).get("notes", "") == ""
