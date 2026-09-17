"""The indexed corpus of a world (spec 12 §5b): pron keeps the index fresh against the store
and retrieves from it."""

from __future__ import annotations

from pron.corpus import Corpus, IndexProjection, fields_text
from corpus.restaurant_corpus import corpus_of, fields_of


# -- the index is kept fresh against the store --------------------------------------------


def test_indexing_twice_reuses_everything_and_embeds_nothing(world, tmp_path):
    corpus = corpus_of(world)
    first = corpus.refresh()
    second = corpus.refresh()
    assert first["embedded"] == len(corpus.entries())
    assert second["embedded"] == 0
    assert second["reused"] == first["embedded"]


def test_an_audit_reports_what_the_index_is_missing(world):
    corpus = corpus_of(world)
    corpus.refresh()
    clean = corpus.audit()
    assert clean["clean"] and not clean["missing"] and not clean["orphan"]
    assert clean["corpus"] == clean["indexed"] == len(corpus.entries())


def test_a_document_that_leaves_the_corpus_is_dropped_from_the_index(world):
    corpus = corpus_of(world)
    corpus.refresh()
    narrower = Corpus(
        world,
        IndexProjection.of(exclude_models=["Table"], text=fields_of, text_id="fields"),
    )
    narrower.matcher = corpus.matcher
    narrower._index = corpus.index
    report = narrower.refresh()
    assert report["dropped"] > 0
    assert narrower.audit()["clean"]


def test_refresh_if_stale_does_nothing_when_the_index_matches(world):
    corpus = corpus_of(world)
    corpus.refresh()
    assert corpus.refresh_if_stale() is None


def test_another_text_projection_keeps_its_own_index_file(world):
    a = corpus_of(world)
    b = corpus_of(world, text=fields_text("notes", "zone"), text_id="notes")
    assert a.index_path != b.index_path
    assert "fields" in a.index_path.name
    assert "notes" in b.index_path.name


# -- retrieval ----------------------------------------------------------------------------


def test_a_rank_returns_documents_by_their_export_id(world):
    corpus = corpus_of(world)
    corpus.refresh()
    entries = corpus.entries()
    assert entries
    hits = corpus.rank(entries[0].text, k=3)
    assert hits
    assert hits[0].id == entries[0].id
    assert hits[0].payload
    assert all(h.score >= hits[-1].score for h in hits)


def test_a_rank_can_be_restricted_to_a_subset(world):
    corpus = corpus_of(world)
    corpus.refresh()
    entries = corpus.entries()
    allowed = [entries[1].id]
    hits = corpus.rank(entries[0].text, among=allowed)
    assert {h.id for h in hits} <= set(allowed)


def test_a_threshold_leaves_out_what_is_below_it(world):
    corpus = corpus_of(world)
    corpus.refresh()
    assert corpus.rank("zzzz qqqq xxxx", threshold=0.99) == []
