"""Referents a read leaves (spec 06): the one document the sentence named is the singular
antecedent of its class, besides the answer it gave."""

from __future__ import annotations

from pron.session import Session
from worlds.restaurant import build_restaurant

NOW = "2026-09-09"
ANA = "st.{Client}.client-ana-perez"


def test_the_named_subject_of_a_read_is_the_singular_referent(tmp_path):
    session = Session(build_restaurant(tmp_path), speaker="jp", now=NOW)
    read = session.turn("what reservations does Ana Pérez have?")
    assert read.outcome == "unico", read.text
    assert session.dialogue.singular.get("Client") == ANA
    r = session.turn("book her a table on the terrace for 6 people on Friday at 9pm")
    assert r.outcome == "unico", r.text
    store = session.world.store
    assert store.doc("Reservation", "reservation-2026-09-11-ana-perez") is not None
