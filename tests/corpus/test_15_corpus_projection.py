"""The indexed corpus of a world (spec 12 §5b): the consumer declares which documents it
retrieves and what text represents one; every entry is identified as the world exports it."""

from __future__ import annotations

from pron.corpus import fields_text, summary_text
from pron.kernel.ids import join_id, split_id
from corpus.restaurant_corpus import corpus_of


# -- the projection is the only thing the consumer declares -------------------------------


def test_the_projection_selects_the_models_that_enter_the_corpus(world):
    every = {e.model for e in corpus_of(world).entries()}
    assert {"Client", "Table", "Reservation"} <= every
    only_tables = {e.model for e in corpus_of(world, models=["Table"]).entries()}
    assert only_tables == {"Table"}


def test_a_model_can_be_excluded_without_naming_every_other(world):
    dropped = "Table"
    rest = {e.model for e in corpus_of(world, exclude_models=[dropped]).entries()}
    assert dropped not in rest


def test_the_text_of_a_document_is_the_consumers_business(world):
    payload = {"summary": "a summary", "description": "a description"}
    assert summary_text(payload) == "a summary"
    assert fields_text("description", "summary")(payload) == "a description"
    assert fields_text("absent", "summary")(payload) == "a summary"
    assert fields_text("absent")(payload) == ""


def test_a_document_without_representative_text_stays_out(world):
    corpus = corpus_of(world, text=lambda p: "", text_id="nothing")
    assert corpus.entries() == []


# -- identity is always the export id -----------------------------------------------------


def test_every_entry_is_identified_as_the_world_exports_it(world):
    for entry in corpus_of(world).entries():
        assert entry.id == join_id(entry.store, entry.model, entry.name)
        assert entry.id != entry.name


def test_an_entry_carries_its_parts_so_no_consumer_splits_an_id(world):
    """A document name may itself hold a colon (a RelationDoc is named after the two ends
    it joins), and then an export id cannot be split back: 'RelationDoc:r--A:b' reads as
    store 'RelationDoc'. An entry carries store, model and name apart for that reason."""
    entries = {e.name: e for e in corpus_of(world).entries()}
    tricky = [e for n, e in entries.items() if ":" in n]
    assert tricky, "the restaurant has relation documents"
    for entry in tricky:
        assert split_id(entry.id)[1] != entry.model  # the ambiguity, stated
        assert entry.model == "RelationDoc"


def test_the_hash_of_an_entry_is_the_stores_content_hash(world):
    for entry in corpus_of(world).entries()[:3]:
        assert entry.hash == world.store.hash_c(entry.model, entry.name, entry.store)
