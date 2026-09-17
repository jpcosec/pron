"""The conversation of spec 09 on a fresh world each: undo of a move with several writes to
one document, a display template with a missing value, a possessive referent."""

from __future__ import annotations

from pron.session import Session
from worlds.restaurant import build_restaurant

NOW = "2026-09-09"
LUIS = ("Reservation", "reservation-2026-09-11-luis-soto")


def test_undo_restores_every_write_of_a_move_to_the_same_document(tmp_path):
    """Spec 11 §7: a document is 'changed after that move' only if something outside the move
    changed it; two writes of one move to one reservation are both undone."""
    s = Session(build_restaurant(tmp_path), projection="all", speaker="jp", now=NOW)
    before = dict(s.world.store.payload(*LUIS))
    s.turn("the reservation of Luis Soto")  # 'it' in the move below needs an antecedent
    r = s.turn(
        "change the reservation of Luis Soto to 9 people and add a note saying: birthday"
    )
    assert r.outcome == "unico" and len(r.record["writes"]) == 2, r.text
    r = s.turn("undo the last move")
    assert "changed after" not in r.text and "Heads up" not in r.text, r.text
    after = s.world.store.payload(*LUIS)
    assert (after["party_size"], after["notes"]) == (
        before["party_size"],
        before["notes"],
    )


def test_a_display_template_drops_the_part_whose_value_is_missing(tmp_path):
    """Spec 09a: without an edge the template's gap stays empty; the name does not keep the
    label and separator around it ('table , pending')."""
    s = Session(build_restaurant(tmp_path), projection="all", speaker="jp", now=NOW)
    r = s.eval(
        '(create Reservation (as "walk-in") (date "2026-09-12") (time "13:00") (party_size 2))'
    )
    assert r.text == "Created reservation 2026-09-12 13:00, 2 people, pending.", r.text


def test_a_possessive_referent_names_the_subject_not_the_value(tmp_path):
    """Spec 04/10 "remove its provenance", spec 06 referents: 'its' is the referent whose field
    is removed whole, as in 'remove the notes of it'; it is not the value to remove."""
    s = Session(build_restaurant(tmp_path), projection="all", speaker="jp", now=NOW)
    assert (
        s.eval('(change (doc "Client:client-luis-soto") notes "vegan")').outcome
        == "unico"
    )
    r = s.turn("remove its notes")
    assert r.outcome == "unico", r.text
    assert (
        r.record["forms"] == '(remove (it "its") notes)'
    )  # notes: Client and Reservation
    assert r.record["writes"][0]["before"] == "vegan"
    assert s.world.store.payload("Client", "client-luis-soto").get("notes", "") == ""
