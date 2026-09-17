"""Characterization (golden master, spec 07 and 11 §7): why and undo after every kind of write —
change, add, remove with and without a value, clean, forget, create and a composed move —
recorded whole, with what each undo leaves in the store, as they are today."""

from __future__ import annotations

from golden.run import play, restaurant

ANCHOR = '(doc "AnchorDoc:anchor-client")'
UNDO = "undo the last move"

LISTS = [
    ("eval", f"(show {ANCHOR})"),
    "add patron to its forms",
    "why?",
    UNDO,
    "add patron to its forms",
    "remove patron from its forms",
    "why?",
    UNDO,
    ("eval", f'(change {ANCHOR} forms (list "client" "client" "" "clients"))'),
    "clean its forms",
    "why?",
    UNDO,
    "remove the forms",
    "why?",
    UNDO,
    "why?",
]

DOCUMENTS = [
    UNDO,
    "create a client named Eva Diaz, phone 9 4444 0000",
    "why?",
    UNDO,
    "change the reservation of Luis Soto to 3 people",
    "why?",
    UNDO,
    "change the reservation of Luis Soto to 9 people and add a note saying: birthday",
    "why?",
    UNDO,
    "forget table 20",
    "why?",
    UNDO,
    "create a client named Ana Rojas, phone 9 5555 1234",
    "book her a table on the terrace for 6 people on Friday at 9pm",
    "why?",
    UNDO,
    "confirm it",  # the undo removed the reservation: 'it' has no antecedent
    "why?",
    UNDO,  # undo again: the move before, the create of Ana Rojas
]


def test_undo_and_why_on_list_fields(tmp_path, snapshot):
    _, session = restaurant(tmp_path, projection="keeper")
    assert play(session, LISTS, tmp_path) == snapshot


def test_undo_and_why_on_documents(tmp_path, snapshot):
    _, session = restaurant(tmp_path)
    assert play(session, DOCUMENTS, tmp_path) == snapshot
