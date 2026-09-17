"""Characterization (golden master, spec 09 and patterns.yaml): the whole observable output of
the conversation of spec 09 and of every construction pron understands, turn by turn, as it is
today. A refactor that changes one answer, trace line, record key or written payload fails here;
if the change is intended, review the diff and run with --snapshot-update."""

from __future__ import annotations

from golden.run import play, restaurant

SPEC_09 = [
    "create a client named Ana Rojas, phone 9 5555 1234",
    "book her a table on the patio for 6 people on Friday at 9pm",
    "on the terrace",
    "what reservations does Ana have for Friday?",
    "Rojas",
    "confirm it",
    "change it to 9 people and add a note saying: birthday",
    "why did you warn me about the table?",
]

# one sentence per construction of patterns.yaml, in its order where the world allows
CONSTRUCTIONS = [
    "undo the last move",  # undo, with nothing to undo yet
    "refresh",  # refresh
    "why?",  # why, with nothing said yet
    "create a client named Ana Rojas, phone 9 5555 1234",  # create
    "book her a table on the terrace for 6 people on Friday at 9pm",  # compose
    "confirm it",  # action_alias
    "change it to 9 people",  # change_to
    "add a note saying: birthday",  # set_field
    "why?",  # why
    "undo the last move",  # undo
    ("eval", '(show (doc "AnchorDoc:anchor-client"))'),
    "add patron to its forms",  # list_op
    "forget table 5",  # forget
    "forget that reservation",  # forget, ambiguous
    "none",
    (
        "eval",
        '(create Reservation (as "walk-in") (date "2026-09-12") (time "13:00") (party_size 2))',
    ),
    "assign it to table 20",  # assert_relation
    "what reservations does Luis Soto have for Friday?",  # read_relation
    "the large tables on the terrace",  # nominal
    "refresh",
]


def test_spec_09_conversation(tmp_path, snapshot):
    _, session = restaurant(tmp_path)
    assert play(session, SPEC_09, tmp_path) == snapshot


def test_every_construction(tmp_path, snapshot):
    _, session = restaurant(tmp_path, projection="keeper")
    assert play(session, CONSTRUCTIONS, tmp_path) == snapshot
