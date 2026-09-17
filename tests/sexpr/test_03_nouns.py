"""Step 3: a noun phrase is a scope plus predicates, answered by sldb; the determiner decides."""

from __future__ import annotations

import pytest

from pron.world.lexicon import Lexicon
from pron.sexpr.resolving.resolve import resolve
from pron.surface.nouns import find_noun_phrases
from pron.surface.classifier import Classifier
from pron.world.world import World
from worlds.restaurant import build_restaurant

NOW = "2026-09-09"


@pytest.fixture(scope="module")
def world(tmp_path_factory) -> World:
    return build_restaurant(tmp_path_factory.mktemp("restaurant"))


@pytest.fixture(scope="module")
def lex(world: World) -> Lexicon:
    return Lexicon(world, world.projection("all"))


@pytest.fixture(scope="module")
def clf(lex: Lexicon) -> Classifier:
    return Classifier(lex, now=NOW)


def phrase(clf, lex, text):
    nps = find_noun_phrases(clf.classify(text), lex)
    assert nps, text
    return nps[0]


def test_classification_keeps_ambiguity_and_fills_slots(clf: Classifier):
    items = clf.classify("a table on the terrace for 6 people")
    kinds = [i.kind for i in items]
    assert kinds == ["det", "word", "word", "word"]
    assert items[2].slots == {"Z": "terrace"}
    assert {w.ref for w in items[3].words} == {
        "(field Reservation party_size)",
        '(where Table "capacity >= N")',
    }
    assert items[3].slots == {"N": 6}


def test_plural_phrase_with_two_predicates_is_two_queries_and_an_intersection(clf, lex):
    np = phrase(clf, lex, "the large tables on the terrace")
    assert np.model == "Table" and np.number == "plural"
    assert np.predicates == ["capacity >= 6", 'zone = "terrace"']
    r = resolve(np, lex)
    assert r.outcome == "unico" and r.addresses == [
        "st.{Table}.table-12",
        "st.{Table}.table-14",
    ]
    assert (
        len(r.queries) == 3
        and r.queries[0].startswith("find 'st.{Table+}' --where 'capacity >= 6'")
        and r.queries[2] == "∩ → 2"
    )


def test_a_modifier_of_another_model_is_left_for_the_sentence(clf, lex):
    np = phrase(clf, lex, "a table on the terrace for 6 people")
    assert np.predicates == ['zone = "terrace"', "capacity >= 6"]
    r = resolve(np, lex)
    assert (
        r.outcome == "unico"
        and r.addresses == ["st.{Table}.table-12"]
        and r.candidates == ["st.{Table}.table-14"]
    )


def test_key_field_names_an_object(clf, lex):
    r = resolve(phrase(clf, lex, "table 12"), lex)
    assert r.outcome == "unico" and r.addresses == ["st.{Table}.table-12"]
    assert r.queries == ["find 'st.{Table+}' --where 'number = 12' → 1"]
    r = resolve(phrase(clf, lex, "a table on the terrace for 6 people"), lex)
    assert (
        r.outcome == "unico"
        and r.addresses == ["st.{Table}.table-12"]
        and "also" in r.note
    )


def test_singular_with_two_matches_is_ambiguous_with_candidates(clf, lex, world):
    assert resolve(phrase(clf, lex, "the client Ana"), lex).outcome == "unico"
    world.store.create(
        "Client",
        "client-ana-rojas",
        {"name": "Ana Rojas", "phone": "9 5555 1234", "notes": ""},
        world.root / "clients" / "ana-rojas.md",
    )
    r = resolve(phrase(clf, lex, "the client Ana"), lex)
    assert r.outcome == "ambiguo"
    assert r.candidates == [
        "st.{Client}.client-ana-perez",
        "st.{Client}.client-ana-rojas",
    ]


def test_plural_without_predicates_is_the_whole_class_and_empty_is_still_unique(
    clf, lex
):
    r = resolve(phrase(clf, lex, "the tables"), lex)
    assert r.outcome == "unico" and len(r.addresses) == 5
    r = resolve(phrase(clf, lex, "the seated reservations"), lex)
    assert r.outcome == "unico" and r.addresses == []


def test_unknown_enum_value_is_missing_before_any_query(clf, lex):
    np = phrase(clf, lex, "a table on the terace")
    assert np.unknown_values == [("Table", "zone", "terace")]
    r = resolve(np, lex)
    assert r.outcome == "missing" and r.queries == [] and r.candidates == ["terrace"]


def test_unknown_proper_name_is_missing_after_the_query(clf, lex):
    r = resolve(phrase(clf, lex, "the client Zoe"), lex)
    assert (
        r.outcome == "missing" and r.queries and "Zoe" in r.queries[0] + r.queries[-1]
    )


def test_interrogated_and_referent_phrases(clf, lex):
    items = clf.classify("what reservations does Ana have for Friday?")
    nps = find_noun_phrases(items, lex)
    assert (
        nps[0].model == "Reservation"
        and nps[0].interrogated
        and nps[0].number == "plural"
    )
    items = clf.classify("confirm it")
    nps = find_noun_phrases(items, lex)
    assert nps[0].referent is not None and nps[0].number == "singular"
