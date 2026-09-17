"""Characterization (golden master, spec 01, 07 and 11 §7): what pron refuses and how it says
so — a read-only session, verbs a projection does not allow, a relation condition that does not
hold, an illegal transition, forgetting an endpoint, undo of a document changed since, and a
compose alias that refers to $created before creating it — recorded whole as they are today."""

from __future__ import annotations

from golden.run import LUIS, play, restaurant

WRITES = [
    "the clients",
    "create a client named Zoe Lee, phone 1",
    "confirm the reservation of Luis Soto",
    ("eval", '(create Client (name "X Y") (phone "1"))'),
]

NOT_ALLOWED = [
    "change the reservation of Luis Soto to 5 people",
    ("eval", '(forget (doc "Table:table-20"))'),
    "the client Luis Soto",
    "book him a table on the terrace for 2 people on Saturday at 8pm",
]


def _changed_outside(world) -> str:
    world.store.update_field("Reservation", LUIS.split(":")[1], "party_size", 7)
    return "party_size of Luis Soto's reservation set to 7 outside pron"


REFUSED = [
    (
        "eval",
        '(create Reservation (as "walk-in") (date "2026-09-12") (time "20:00") (party_size 6))',
    ),
    "assign it to table 20",
    ("eval", '(assert assigned_to (doc "Reservation:walk-in") (doc "Table:table-20"))'),
    ("eval", f'(change (doc "{LUIS}") status "seated")'),
    "forget the client Luis Soto",
    "change the reservation of Luis Soto to 5 people",
    ("outside", _changed_outside),
    "undo the last move",
    "the reservation of Luis Soto",
    "change it to 100 people and confirm it",  # the move is validated whole
    "the client Luis Soto",
    "prebook him on Friday at 9pm for 2 people",
    (
        "eval",
        '(say prebook (slot "$referent:Client" (doc "Client:client-luis-soto")) (party_size 2))',
    ),
]


def test_read_only_session(tmp_path, snapshot):
    _, session = restaurant(tmp_path, read_only=True)
    assert play(session, WRITES, tmp_path) == snapshot


def test_verbs_the_projection_does_not_allow(tmp_path, snapshot):
    _, session = restaurant(tmp_path, projection="creator")
    assert play(session, NOT_ALLOWED, tmp_path) == snapshot


def test_refused_writes(tmp_path, snapshot):
    _, session = restaurant(tmp_path)
    assert play(session, REFUSED, tmp_path) == snapshot
