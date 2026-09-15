"""The indexed corpus of a world (spec 12 §5b): the consumer declares which documents it
retrieves and what text represents one, pron does the rest."""

from __future__ import annotations

import pytest

from pron.corpus import Corpus, CorpusEntry, IndexProjection, fields_text, summary_text
from pron.ids import join_id, split_id
from pron.world import World
from worlds.restaurant import build_restaurant


@pytest.fixture(scope="module")
def world(tmp_path_factory) -> World:
    return build_restaurant(tmp_path_factory.mktemp("restaurant"))


def _text(payload: dict) -> str:
    """The restaurant has no summaries: a document reads as its own fields."""
    return " ".join(f"{k} {v}" for k, v in payload.items() if isinstance(v, (str, int)))


def _corpus(world: World, **kw) -> Corpus:
    kw.setdefault("text", _text)
    kw.setdefault("text_id", "fields")
    return Corpus(world, IndexProjection.of(**kw))


# -- the projection is the only thing the consumer declares -------------------------------


def test_the_projection_selects_the_models_that_enter_the_corpus(world):
    every = {e.model for e in _corpus(world).entries()}
    assert {"Client", "Table", "Reservation"} <= every
    only_tables = {e.model for e in _corpus(world, models=["Table"]).entries()}
    assert only_tables == {"Table"}


def test_a_model_can_be_excluded_without_naming_every_other(world):
    dropped = "Table"
    rest = {e.model for e in _corpus(world, exclude_models=[dropped]).entries()}
    assert dropped not in rest


def test_the_text_of_a_document_is_the_consumers_business(world):
    payload = {"summary": "a summary", "description": "a description"}
    assert summary_text(payload) == "a summary"
    assert fields_text("description", "summary")(payload) == "a description"
    assert fields_text("absent", "summary")(payload) == "a summary"
    assert fields_text("absent")(payload) == ""


def test_a_document_without_representative_text_stays_out(world):
    corpus = _corpus(world, text=lambda p: "", text_id="nothing")
    assert corpus.entries() == []


# -- identity is always the export id -----------------------------------------------------


def test_every_entry_is_identified_as_the_world_exports_it(world):
    for entry in _corpus(world).entries():
        assert entry.id == join_id(entry.store, entry.model, entry.name)
        assert entry.id != entry.name


def test_an_entry_carries_its_parts_so_no_consumer_splits_an_id(world):
    """A document name may itself hold a colon (a RelationDoc is named after the two ends
    it joins), and then an export id cannot be split back: 'RelationDoc:r--A:b' reads as
    store 'RelationDoc'. An entry carries store, model and name apart for that reason."""
    entries = {e.name: e for e in _corpus(world).entries()}
    tricky = [e for n, e in entries.items() if ":" in n]
    assert tricky, "the restaurant has relation documents"
    for entry in tricky:
        assert split_id(entry.id)[1] != entry.model  # the ambiguity, stated
        assert entry.model == "RelationDoc"


def test_the_hash_of_an_entry_is_the_stores_content_hash(world):
    for entry in _corpus(world).entries()[:3]:
        assert entry.hash == world.store.hash_c(entry.model, entry.name, entry.store)


# -- the index is kept fresh against the store --------------------------------------------


def test_indexing_twice_reuses_everything_and_embeds_nothing(world, tmp_path):
    corpus = _corpus(world)
    first = corpus.refresh()
    second = corpus.refresh()
    assert first["embedded"] == len(corpus.entries())
    assert second["embedded"] == 0
    assert second["reused"] == first["embedded"]


def test_an_audit_reports_what_the_index_is_missing(world):
    corpus = _corpus(world)
    corpus.refresh()
    clean = corpus.audit()
    assert clean["clean"] and not clean["missing"] and not clean["orphan"]
    assert clean["corpus"] == clean["indexed"] == len(corpus.entries())


def test_a_document_that_leaves_the_corpus_is_dropped_from_the_index(world):
    corpus = _corpus(world)
    corpus.refresh()
    narrower = Corpus(
        world,
        IndexProjection.of(exclude_models=["Table"], text=_text, text_id="fields"),
    )
    narrower.matcher = corpus.matcher
    narrower._index = corpus.index
    report = narrower.refresh()
    assert report["dropped"] > 0
    assert narrower.audit()["clean"]


def test_refresh_if_stale_does_nothing_when_the_index_matches(world):
    corpus = _corpus(world)
    corpus.refresh()
    assert corpus.refresh_if_stale() is None


def test_another_text_projection_keeps_its_own_index_file(world):
    a = _corpus(world)
    b = _corpus(world, text=fields_text("notes", "zone"), text_id="notes")
    assert a.index_path != b.index_path
    assert "fields" in a.index_path.name
    assert "notes" in b.index_path.name


# -- retrieval ----------------------------------------------------------------------------


def test_a_rank_returns_documents_by_their_export_id(world):
    corpus = _corpus(world)
    corpus.refresh()
    entries = corpus.entries()
    assert entries
    hits = corpus.rank(entries[0].text, k=3)
    assert hits
    assert hits[0].id == entries[0].id
    assert hits[0].payload
    assert all(h.score >= hits[-1].score for h in hits)


def test_a_rank_can_be_restricted_to_a_subset(world):
    corpus = _corpus(world)
    corpus.refresh()
    entries = corpus.entries()
    allowed = [entries[1].id]
    hits = corpus.rank(entries[0].text, among=allowed)
    assert {h.id for h in hits} <= set(allowed)


def test_a_threshold_leaves_out_what_is_below_it(world):
    corpus = _corpus(world)
    corpus.refresh()
    assert corpus.rank("zzzz qqqq xxxx", threshold=0.99) == []


# -- the life cycle of a world is pron's business -----------------------------------------


def test_a_built_world_is_ready_and_ensuring_it_again_does_nothing(world):
    assert world.is_ready()
    assert world.ensure_ready() is None


def test_ensure_ready_makes_a_plain_store_a_world(tmp_path):
    from sldb.cli.main import main as sldb_main

    root = tmp_path / "plain"
    root.mkdir()
    assert sldb_main(["stores", "init", "--path", str(root)]) == 0
    plain = World(root)
    assert not plain.is_ready()
    report = plain.ensure_ready()
    assert report is not None
    assert plain.is_ready()
