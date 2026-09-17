"""Step 2: the lexicon is derived from the store and cut by the projection; nothing of a world is in code."""

from __future__ import annotations

import pytest

from pron.world.lexicon import Lexicon
from pron.world.world import World
from worlds.restaurant import build_restaurant


@pytest.fixture(scope="module")
def world(tmp_path_factory) -> World:
    return build_restaurant(tmp_path_factory.mktemp("restaurant"))


@pytest.fixture(scope="module")
def lex(world: World) -> Lexicon:
    return Lexicon(world, world.projection("all"))


def test_every_word_has_a_source_in_the_store_and_a_motive(lex: Lexicon):
    assert lex.words
    for w in lex.words:
        assert w.motive.strip(), w
        assert w.source.startswith(
            (
                "model ",
                "field ",
                "enum ",
                "used value",  # PLAN 11 P3: an already-used value of system/tags
                "RelationTypeDoc ",
                "AnchorDoc ",
                "kernel",
            )
        ), w


def test_models_fields_values_relations_and_aliases_enter(lex: Lexicon):
    assert {w.ref for w in lex.lookup("table")} == {"(model Table)"}
    assert lex.lookup("party size")[0].motive == "Number of people coming."
    assert {w.ref for w in lex.lookup("terrace")} == {'(value Table zone "terrace")'}
    assert lex.lookup("assigned to")[0].payload["mode"] == "read and assert"
    assert lex.lookup("book her")[0].kind == "alias-compose"
    assert (
        lex.lookup("confirm it")[0].ref
        == '(change (it "it" Reservation) status "confirmed")'
    )


def test_kernel_verbs_are_cut_by_the_projection(world: World, lex: Lexicon):
    assert lex.lookup("undo the last move")[0].payload["verb"] == "undo"
    read_only = dict(
        world.projection("all"),
        actions=[],
        relations=[{"name": "booked_by", "mode": "read"}],
    )
    lex2 = Lexicon(world, read_only)
    assert lex2.lookup("create") == []
    assert lex2.lookup("assigned to") == []
    assert lex2.lookup("booked by")[0].payload["mode"] == "read"


def test_verbs_of_a_class_are_derived_not_registered(lex: Lexicon):
    refs = {w.ref for w in lex.verbs_for("Reservation")}
    assert {
        "(relation booked_by)",
        "(relation assigned_to)",
        "(action change)",
        "(action forget)",
        '(move (create Reservation) (assert booked_by (created) (it "it" Client)) (assert assigned_to (created) (a Table)))',
        '(change (it "it" Reservation) status "confirmed")',
    } <= refs
    assert "(relation transitions_to)" not in refs
    table_refs = {w.ref for w in lex.verbs_for("Table")}
    assert (
        "(relation assigned_to)" in table_refs
        and '(change (it "it" Reservation) status "confirmed")' not in table_refs
    )


def test_near_offers_neighbors_and_never_executes(lex: Lexicon):
    # without an embedder, string similarity: typos are caught, synonyms are not
    assert lex.matcher.id() == "difflib"
    near = lex.near("terace", kinds=("value",))
    assert near and near[0][0].form == "terrace"
    near_word = lex.near("reservtion")
    assert near_word[0][0].ref == "(model Reservation)"
    assert lex.near("patio", kinds=("value",)) == []


class FakeEmbedder:
    """A stand-in for the port: two hand-made dimensions, 'outdoors' and 'inside'."""

    def id(self) -> str:
        return "fake"

    def embed(self, texts):
        out = []
        for t in texts:
            t = t.lower()
            outdoors = (
                1.0
                if any(
                    w in t
                    for w in ("patio", "terrace", "outdoor", "open-air", "garden")
                )
                else 0.0
            )
            inside = 1.0 if any(w in t for w in ("indoor", "inside", "room")) else 0.0
            out.append([outdoors, inside, 0.1])
        return out


def test_an_injected_embedder_finds_synonyms(world: World):
    from pron.world.matcher import Matcher

    lex = Lexicon(world, world.projection("all"), matcher=Matcher(FakeEmbedder()))
    near = lex.near("patio", kinds=("value",))
    assert near and near[0][0].form == "terrace"
    assert lex.matcher.id() == "fake"


def test_an_injected_embedder_keeps_typos_near(world: World):
    """With an Embedder, a misspelling is still offered: the score is the best of meaning
    (cosine) and spelling (difflib), never only the vector (spec 11 §2: better with
    embeddings, never worse)."""
    from pron.world.matcher import Matcher

    class Orthogonal:
        def id(self) -> str:
            return "orthogonal"

        def embed(self, texts):
            return [[1.0, 0.0] if t == "reservtion" else [0.0, 1.0] for t in texts]

    ranked = Matcher(Orthogonal()).rank(
        "reservtion", [("r", "reservation"), ("z", "zone")], threshold=0.55
    )
    assert ranked and ranked[0][0] == "r"
