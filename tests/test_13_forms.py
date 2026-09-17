"""Forms (spec 13): pron's structured moves. The reader and printer round-trip; a runtime that knows
its documents evaluates forms directly with the same checks as a sentence; and a sentence is the
forms it resolves to: evaluating the forms a conversation recorded, on a second copy of the world,
leaves the same writes."""

from __future__ import annotations

import pytest

from pron.session import Session
from pron.kernel.sexp import Sym, read, read_one, write
from pron.world.world import World
from worlds.restaurant import build_restaurant

NOW = "2026-09-09"
LUIS = "Reservation:reservation-2026-09-11-luis-soto"


@pytest.fixture(scope="module")
def world(tmp_path_factory) -> World:
    return build_restaurant(tmp_path_factory.mktemp("forms"))


def session(world: World, **kw) -> Session:
    return Session(world, projection="all", speaker="runtime", now=NOW, **kw)


def test_reader_and_printer_round_trip():
    text = '(move (change (doc "Reservation:r-1") party_size 9) (add (doc "Client:c") tags (list "a" "b \\"q\\"")) (create Table (number 7) (capacity 2.5) (zone nil) (open true)))'
    expr = read_one(text)
    assert expr[0] == Sym("move") and isinstance(expr[1][1][1], str)
    assert read_one(write(expr)) == expr
    assert len(read("(undo) (refresh)")) == 2


def test_a_read_by_address_and_by_predicate(world: World):
    s = session(world)
    r = s.eval('(show (find Table (where "capacity >= 6")))')
    assert r.outcome == "unico", r.text
    assert "table 12" in r.text.lower() and "table 14" in r.text.lower()
    r = s.eval(f'(targets assigned_to (doc "{LUIS}"))')
    assert r.outcome == "unico" and "3" in r.text, r.text


def test_the_is_ambiguous_and_asks_like_a_sentence(world: World):
    s = session(world)
    r = s.eval('(show (the Table (where "zone = \\"terrace\\"")))')
    assert r.outcome == "ambiguo" and "table 12" in r.text
    assert any("table-14" in c for c in r.record["candidates"])
    r = s.turn("table 14")
    assert r.outcome == "unico" and "14" in r.text, r.text


def test_an_assertion_goes_through_the_condition(world: World):
    s = session(world)
    r = s.eval(f'(assert assigned_to (doc "{LUIS}") (doc "Table:table-20"))')
    # table 20 seats 2 and the party is 4; and luis already has a table: cardinality many_to_one
    assert r.outcome == "error"
    assert not r.record["writes"]


def test_a_transition_is_checked_and_undone(world: World):
    s = session(world)
    r = s.eval(f'(change (doc "{LUIS}") status "seated")')
    assert r.outcome == "error" and "transition" in r.text, r.text
    r = s.eval(f'(say confirm (doc "{LUIS}"))')
    assert r.outcome == "unico", r.text
    assert world.store.payload_of(LUIS)["status"] == "confirmed"
    move = world.store.payload("MoveDoc", r.move_id)
    assert move["sentence"] == f'(say confirm (doc "{LUIS}"))'
    r = s.eval("(undo)")
    assert r.outcome == "unico", r.text
    assert world.store.payload_of(LUIS)["status"] == "pending"


def test_words_outside_the_projection_do_not_exist(world: World):
    s = session(world)
    assert s.eval('(show (doc "Nope:x"))').outcome == "missing"
    assert s.eval('(show (doc "Table:table-99"))').outcome == "missing"
    r = s.eval('(assert nope (doc "Table:table-3") (doc "Table:table-5"))')
    assert r.outcome == "missing" and "nope" in r.text
    assert session(world, read_only=True).eval(
        '(create Client (name "X Y") (phone "1"))'
    ).outcome in ("error", "missing")
    assert s.eval("(explode)").outcome == "error"
    assert s.eval("(show").outcome == "error"


def test_a_bare_noun_suggests_show(world: World):
    """A noun alone is not a move (spec 13): the error proposes the (show …) move it needs; an
    unknown head close to a known one proposes it, a foreign one proposes nothing."""

    s = session(world)
    r = s.eval("(all Table)")
    assert r.outcome == "error" and "(show (all Table))" in r.text
    r = s.eval('(doc "Table:table-3")')
    assert r.outcome == "error" and '(show (doc "Table:table-3"))' in r.text
    r = s.eval("(shwo (all Table))")
    assert r.outcome == "error" and "did you mean (show …)" in r.text
    r = s.eval("(explode)")
    assert r.outcome == "error" and "did you mean" not in r.text


def test_a_sentence_is_the_forms_it_records(tmp_path_factory):
    """The conversation of spec 09 on one world; the resolved forms it recorded, evaluated on another
    copy, leave the same writes and the same answers."""
    spoken = build_restaurant(tmp_path_factory.mktemp("spoken"))
    replayed = build_restaurant(tmp_path_factory.mktemp("replayed"))
    talk = Session(spoken, projection="all", speaker="jp", now=NOW)
    run = Session(replayed, projection="all", speaker="jp", now=NOW)
    sentences = [
        "create a client named Ana Rojas, phone 9 5555 1234",
        "book her a table on the terrace for 6 people on Friday at 9pm",
        "confirm it",
        "change it to 9 people and add a note saying: birthday",
        "what reservations does Luis Soto have for Friday?",
    ]
    for sentence in sentences:
        said = talk.turn(sentence)
        assert said.outcome == "unico", (sentence, said.text)
        forms = said.record["resolved"]
        again = run.eval(forms)
        assert again.outcome == "unico", (forms, again.text)
        assert _writes(again.record["writes"]) == _writes(said.record["writes"]), forms
        assert again.text == said.text, forms


def _writes(ws):
    return [
        (w.get("verb"), w.get("address"), w.get("field"), w.get("after")) for w in ws
    ]


def test_a_document_can_be_named_where_the_projection_has_no_rule(world: World):
    s = session(world)
    r = s.eval('(create Table (number 7) (capacity 2) (zone "indoor"))')
    assert r.outcome == "error" and "say the name" in r.text
    r = s.eval('(create Table (as "table-7") (number 7) (capacity 2) (zone "indoor"))')
    assert r.outcome == "unico", r.text
    assert world.store.payload("Table", "table-7")["capacity"] == 2
    assert r.record["forms"].startswith('(create Table (as "table-7")')


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
    assert w.store.payload_of(LUIS)["status"] == "confirmed"
    assert r.record["resolved"] == f'(say confirm (doc "{LUIS}"))'
