"""Characterization (golden master, spec 05 and 06): the dialogue's edge paths — a pending
choice answered, not matched, cancelled and dropped by a new order; a pending data question; a
missing word with near words; a missing value with value suggestions; the correction of the last
missing turn — recorded whole as they are today."""

from __future__ import annotations

from golden.run import play, restaurant
from pron.session import Session
from worlds.values import build_values

ANA = "create a client named Ana Rojas, phone 9 5555 1234"
WHICH_ANA = "what reservations does Ana have?"

PENDING_CHOICE = [
    ANA,
    "book her a table on the terrace for 6 people on Friday at 9pm",
    WHICH_ANA,
    "Garcia",  # matches no candidate: still pending
    "Rojas",  # answers it
    WHICH_ANA,
    "none",  # calls it off
    WHICH_ANA,
    "the large tables",  # a noun phrase is not an order: still pending
    "create a client named Eva Diaz, phone 9 4444 0000",  # a new order drops it
    "Rojas",  # nothing pending any more
]

MISSING = [
    "create a client named Zoe Lee",  # Phone?
    "9 3333 4444",
    "create a client named Eva Diaz",
    "none",
    "the tabels",  # a word the projection does not have, with near words
    "book her a table on the patio for 6 people on Friday at 9pm",  # before any her
    ANA,
    "book her a table on the patio for 6 people on Friday at 9pm",  # patio: not a zone
    "on the terrace",  # corrects the missing turn
    "on the terrace",  # nothing left to correct
]


def test_pending_choice(tmp_path, snapshot):
    _, session = restaurant(tmp_path)
    assert play(session, PENDING_CHOICE, tmp_path) == snapshot


def test_missing_and_corrections(tmp_path, snapshot):
    _, session = restaurant(tmp_path)
    assert play(session, MISSING, tmp_path) == snapshot


def test_value_suggestions(tmp_path, snapshot):
    """spec 05 P2: an unknown value alone offers the sentence that resolves it (difflib, no embedder)."""
    world = build_values(tmp_path / "values")
    session = Session(world, projection="all", speaker="probe", now="2026-09-14")
    steps = [
        "evento adverso",
        "the fact about evento_adversso",
        "the fact about evento_adverso",
    ]
    assert play(session, steps, tmp_path) == snapshot
