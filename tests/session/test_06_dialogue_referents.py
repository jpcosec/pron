"""Referents the dialogue keeps (spec 06): the candidate an answer picks is the singular
antecedent of its class."""

from __future__ import annotations

from pron.session import Session
from worlds.restaurant import build_restaurant

NOW = "2026-09-09"


def test_the_picked_candidate_is_the_singular_referent(tmp_path):
    session = Session(build_restaurant(tmp_path), speaker="jp", now=NOW)
    session.turn("create a client named Ana Rojas, phone 9 5555 1234")
    asked = session.turn("what reservations does Ana have?")
    assert asked.outcome == "ambiguo", asked.text
    chosen = session.dialogue.pending.candidates[0]
    session.turn("1")
    assert session.dialogue.singular["Client"] == chosen
