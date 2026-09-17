"""PLAN 11: pron suggests values that already exist (P1-P3), and a projection's own words
build a few examples it can resolve (P4). Never entered as lexicon, never executed on its
own — offered, and usable as said in the next turn (spec 05 §Calce aproximado)."""

from __future__ import annotations

import pytest

from pron.world.lexicon import Lexicon
from pron.sexpr.resolving.resolve import resolve
from pron.session import Session
from pron.surface.nouns import find_noun_phrases
from pron.surface.classifier import Classifier
from pron.world.world import World
from worlds.values import build_values

NOW = "2026-09-14"


@pytest.fixture(scope="module")
def world(tmp_path_factory) -> World:
    return build_values(tmp_path_factory.mktemp("values"))


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


# -- P1: an equality predicate on a string field that matches nothing suggests existing values


def test_a_typo_in_a_value_suggests_the_existing_one(clf, lex):
    np = phrase(clf, lex, "the fact about evento_adversso")
    r = resolve(np, lex)
    assert r.outcome == "missing", r.note
    assert "evento_adverso" in r.candidates, r.candidates


def test_b_a_space_instead_of_underscore_suggests_the_existing_one(clf, lex):
    np = phrase(clf, lex, "the fact about evento adverso")
    r = resolve(np, lex)
    assert r.outcome == "missing", r.note
    assert "evento_adverso" in r.candidates, r.candidates


def test_d_a_field_over_max_values_does_not_suggest_and_the_trace_says_so(
    clf, lex, world
):
    projection = dict(
        world.projection("all"),
        matching={"neighbors": 3, "threshold": 0.55, "max_values": 2},
    )
    capped_lex = Lexicon(world, projection)
    capped_clf = Classifier(capped_lex, now=NOW)
    np = find_noun_phrases(capped_clf.classify("the fact about xyz"), capped_lex)[0]
    r = resolve(np, capped_lex)
    assert r.outcome == "missing" and r.candidates == [], r.candidates
    assert any("max_values" in q for q in r.queries), r.queries


def test_f_free_text_values_never_enter_the_lexicon(lex: Lexicon):
    assert lex.values_of("Fact", "topic") == []
    assert lex.lookup("evento_adverso") == []


# -- P3: values already used in system/tags do enter the lexicon


def test_e_a_used_system_value_is_lexicon_and_resolves(clf, lex):
    words = lex.values_of("Atom", "system")
    assert {w.form for w in words} == {"pron", "legos"}
    assert all(w.source == "used value" for w in words)
    np = phrase(clf, lex, "the atoms of pron")
    r = resolve(np, lex)
    assert r.outcome == "unico", r.note
    assert len(r.addresses) == 2, r.addresses


# -- P2: an unknown word alone, ranked against existing values, offers the resolving sentence


def test_c_a_bare_unknown_word_offers_the_resolving_sentence():
    world = build_values(_module_tmp("c"))
    session = Session(world, projection="all", speaker="probe", now=NOW, read_only=True)
    r = session.turn("evento adverso")
    assert r.outcome == "missing", r.text
    values = r.record["missing"].get("values") or []
    sentences = [v["sentence"] for v in values]
    assert "the fact about evento_adverso" in sentences, (r.text, sentences)
    assert "the fact about evento_adverso" in r.text, r.text


def test_g_an_injected_embedder_finds_what_difflib_cannot():
    world = build_values(_module_tmp("g"))
    session = Session(
        world,
        projection="all",
        speaker="probe",
        now=NOW,
        read_only=True,
        embedder=_FakeEmbedder(),
    )
    r = session.turn("adverse event")
    assert r.outcome == "missing", r.text
    values = r.record["missing"].get("values") or []
    sentences = [v["sentence"] for v in values]
    assert "the fact about evento_adverso" in sentences, (r.text, sentences)
    assert any("fake-v1" in line for line in r.trace), r.trace


class _FakeEmbedder:
    _VECTORS = {
        "adverse": [1.0, 0.0, 0.0, 0.0],
        "evento_adverso": [0.97, 0.2, 0.0, 0.0],
        "medinfo": [0.0, 1.0, 0.0, 0.0],
        "seguimiento": [0.0, 0.0, 1.0, 0.0],
    }

    def id(self) -> str:
        return "fake-v1"

    def embed(self, texts):
        return [self._VECTORS.get(t, [0.0, 0.0, 0.0, 1.0]) for t in texts]


# -- P4: examples() derives from real words, never fabricated


def test_h_examples_use_only_real_words_of_the_world(lex: Lexicon, clf: Classifier):
    exs = lex.examples()
    assert exs
    for sentence in exs:
        items = clf.classify(sentence)
        assert not any(i.kind == "unknown" for i in items), (sentence, items)


def _module_tmp(tag: str):
    import tempfile
    from pathlib import Path

    return Path(tempfile.mkdtemp(prefix=f"pron-values-{tag}-"))


def test_i_an_unknown_word_never_offers_the_ledger_or_pron_bookkeeping(world: World):
    """A projection may list MoveDoc/AnchorDoc/ProjectionDoc (pron's own world does): their
    values (past sentences of this conversation, anchor refs) are never offered."""
    first = Session(world, projection="all", speaker="test", read_only=True)
    first.turn(
        "what is evento_adversso?"
    )  # leaves a MoveDoc sentence in this tmp world
    fresh = Session(world, projection="all", speaker="test", read_only=True)
    for internal in ("MoveDoc", "AnchorDoc", "ProjectionDoc"):
        if internal not in fresh.lex.models:
            fresh.lex.models.append(internal)
    offered = fresh._value_word_suggestions("evento_adversso", [])
    assert offered, "the real Fact value must still be offered"
    assert all(
        model not in {"MoveDoc", "AnchorDoc", "ProjectionDoc"} for model, *_ in offered
    )
    assert not any("what is" in sentence for *_, sentence in offered)
