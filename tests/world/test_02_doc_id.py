"""A document's id as a value (spec 02, 12 §5): `DocId` parses and prints export ids and
addresses, keeps a RelationDoc's name whole, and is what `pron.kernel.ids` is written over."""

from __future__ import annotations

import dataclasses

import pytest

from pron.kernel import ids
from pron.world.doc_id import DocId

RELATION = "likes--Client:ana--B:Table:table-3"


@pytest.mark.parametrize(
    "text, parts",
    [
        ("Table:table-3", (None, "Table", "table-3")),
        ("A:Table:table-3", ("A", "Table", "table-3")),
        ("local:Table:table-3", (None, "Table", "table-3")),
        (f"RelationDoc:{RELATION}", (None, "RelationDoc", RELATION)),
        (f"A:RelationDoc:{RELATION}", ("A", "RelationDoc", RELATION)),
        (f"local:RelationDoc:{RELATION}", (None, "RelationDoc", RELATION)),
    ],
)
def test_parse_reads_the_three_parts(text: str, parts: tuple):
    d = DocId.parse(text)
    assert (d.store, d.model, d.name) == parts


@pytest.mark.parametrize(
    "text", ["Table:table-3", "A:Table:table-3", f"A:RelationDoc:{RELATION}"]
)
def test_str_is_the_export_id_parse_read(text: str):
    assert str(DocId.parse(text)) == text


def test_local_is_no_store_at_all():
    assert DocId("local", "Table", "t") == DocId(None, "Table", "t")
    assert DocId.of("Table", "t", "local").is_local
    assert str(DocId.of("Table", "t", "local")) == "Table:t"
    assert not DocId.of("Table", "t", "A").is_local


def test_a_doc_id_is_a_frozen_hashable_value():
    d = DocId.parse("A:Table:t")
    with pytest.raises(dataclasses.FrozenInstanceError):
        d.name = "u"  # type: ignore[misc]
    assert {d: 1}[DocId("A", "Table", "t")] == 1


def test_what_is_not_an_export_id_is_refused():
    with pytest.raises(ValueError, match="not an export id"):
        DocId.parse("table-3")


def test_a_relation_doc_id_is_only_whole_through_parse():
    """The split blind to the model takes the first two colons, whatever the model is: that
    is `split_id`, as it has always been. `parse` knows a RelationDoc's name has colons."""
    blind = DocId.parse_plain(f"RelationDoc:{RELATION}")
    assert blind.store == "RelationDoc"
    assert DocId.parse_relation("Table:table-3") is None
    assert DocId.parse_relation(f"A:RelationDoc:{RELATION}") == DocId(
        "A", "RelationDoc", RELATION
    )


def test_address_both_ways():
    assert DocId.parse("A:Table:t").address == "A:st.{Table}.t"
    assert DocId.parse("Table:t").address == "st.{Table}.t"
    assert DocId.from_address("A:st.{Table+}.t") == DocId("A", "Table", "t")
    assert DocId.from_address("st.{Table}.t") == DocId(None, "Table", "t")
    assert DocId.from_address("A:Table:t") == DocId("A", "Table", "t")


def test_relativize_drops_only_the_prefix_of_that_same_store():
    d = DocId.parse("A:Table:t")
    assert d.relativize("A") == DocId(None, "Table", "t")
    assert d.relativize("B") == d
    assert DocId.parse("Table:t").relativize("A") == DocId(None, "Table", "t")


def test_qualify_gives_an_unprefixed_id_the_store_it_was_read_from():
    assert DocId.parse("Table:t").qualify("A") == DocId("A", "Table", "t")
    assert DocId.parse("Table:t").qualify("local") == DocId(None, "Table", "t")
    assert DocId.parse("B:Table:t").qualify("A") == DocId("B", "Table", "t")


@pytest.mark.parametrize(
    "export_id", ["Table:t", "A:Table:t", "local:Table:t", f"A:RelationDoc:{RELATION}"]
)
def test_the_string_helpers_are_doc_id_underneath(export_id: str):
    d = DocId.parse_plain(export_id)
    assert ids.split_id(export_id) == (d.store, d.model, d.name)
    assert ids.join_id(d.store, d.model, d.name) == str(d)
    assert ids.address_of(export_id) == d.address
    assert ids.relativize(export_id, "A") == (
        str(d.relativize("A")) if d.store == "A" else export_id
    )


def test_an_id_the_helpers_do_not_move_comes_back_as_written():
    assert ids.relativize("local:Table:t", "A") == "local:Table:t"
    assert ids.qualify("local:Table:t", None) == "local:Table:t"
    assert ids.qualify("Table:t", "A") == "A:Table:t"
    assert ids.split_relation_doc_id(f"A:RelationDoc:{RELATION}") == ("A", RELATION)
    assert ids.split_relation_doc_id("Table:t") is None
