"""Forms (spec 13): a sentence is the forms it resolves to. Evaluating the forms a conversation
recorded, on a second copy of the world, leaves the same writes; a sentence says unresolved
forms and the evaluator resolves them."""

from __future__ import annotations

from pron.session import Session
from worlds.restaurant import build_restaurant

from pron.world.doc_id import DocId

NOW = "2026-09-09"
LUIS = "Reservation:reservation-2026-09-11-luis-soto"


CONVERSATION = [
    "create a client named Ana Rojas, phone 9 5555 1234",
    "book her a table on the terrace for 6 people on Friday at 9pm",
    "confirm it",
    "change it to 9 people and add a note saying: birthday",
    "what reservations does Luis Soto have for Friday?",
]


def _replays_the_same(talk: Session, run: Session, sentence: str) -> None:
    said = talk.turn(sentence)
    assert said.outcome == "unico", (sentence, said.text)
    forms = said.record["resolved"]
    again = run.eval(forms)
    assert again.outcome == "unico", (forms, again.text)
    assert _writes(again.record["writes"]) == _writes(said.record["writes"]), forms
    assert again.text == said.text, forms


def test_a_sentence_is_the_forms_it_records(tmp_path_factory):
    """The conversation of spec 09 on one world; the resolved forms it recorded, evaluated on another
    copy, leave the same writes and the same answers."""
    spoken = build_restaurant(tmp_path_factory.mktemp("spoken"))
    replayed = build_restaurant(tmp_path_factory.mktemp("replayed"))
    talk = Session(spoken, projection="all", speaker="jp", now=NOW)
    run = Session(replayed, projection="all", speaker="jp", now=NOW)
    for sentence in CONVERSATION:
        _replays_the_same(talk, run, sentence)


def _writes(ws):
    return [
        (w.get("verb"), w.get("address"), w.get("field"), w.get("after")) for w in ws
    ]


def test_a_sentence_says_unresolved_forms_and_the_evaluator_resolves_them(
    tmp_path_factory,
):
    w = build_restaurant(tmp_path_factory.mktemp("said"))
    s = Session(w, projection="all", speaker="jp", now=NOW)
    r = s.turn("the reservations of Luis Soto")
    assert (
        r.record["forms"] == '(show (the Reservation (plural) (of-name "Luis" "Soto")))'
    )
    assert r.record["resolved"] == f'(show (doc "{LUIS}"))'
    # a referent in a form resolves against the same dialogue a sentence uses
    r = s.eval('(say confirm (it "it" Reservation))')
    assert r.outcome == "unico", r.text
    assert w.store.payload(DocId.parse(LUIS))["status"] == "confirmed"
    assert r.record["resolved"] == f'(say confirm (doc "{LUIS}"))'
