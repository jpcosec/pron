"""The store read and written by `DocId` (spec 02, 04): one form per operation, which the
`(model, name, store)` and `*_of(export_id)` forms delegate to — so the three always agree."""

from __future__ import annotations

import pytest

from pron.world.doc_id import DocId
from pron.world.store_error import StoreError
from pron.world.world import World

TABLE = DocId.parse("Table:table-3")
CLIENT = DocId.parse("Client:client-ana-perez")


def _projection(world: World) -> DocId:
    return DocId.of("ProjectionDoc", world.store.docs_of("ProjectionDoc")[0].name)


def test_the_three_forms_read_the_same_document(world: World):
    store = world.store
    assert store.doc_at(TABLE) is store.doc("Table", "table-3")
    assert store.doc_at(TABLE) is store.doc_of("Table:table-3")
    assert store.payload_at(TABLE) == store.payload("Table", "table-3")
    assert store.payload_at(TABLE) == store.payload_of("local:Table:table-3")
    assert store.hash_at(TABLE) == store.hash_c("Table", "table-3") != ""
    assert store.hash_at(TABLE) == store.hash_of("Table:table-3")
    assert store.path_at(TABLE) == store.doc_path("Table", "table-3")


def test_a_document_that_is_not_there(world: World):
    nobody = DocId.parse("Table:table-999")
    assert world.store.doc_at(nobody) is None
    assert world.store.hash_at(nobody) == "" and world.store.path_at(nobody) is None
    with pytest.raises(StoreError, match="no Table named 'table-999'$"):
        world.store.payload_at(nobody)
    with pytest.raises(StoreError, match="no store linked as 'Z'"):
        world.store.hash_at(nobody.in_store("Z"))


def test_field_writes_return_what_was_there(world: World):
    store = world.store
    capacity = store.payload_at(TABLE)["capacity"]
    assert store.update_field_at(TABLE, "capacity", capacity + 1) == capacity
    assert store.update_field("Table", "table-3", "capacity", capacity) == capacity + 1
    assert store.update_field_of("Table:table-3", "capacity", capacity) == capacity
    assert store.payload_at(TABLE)["capacity"] == capacity


def test_list_writes_and_whole_payload_rewrite(world: World):
    store, everything = world.store, _projection(world)
    before = store.payload_at(everything)
    index = store.append_at(everything, "aliases", "todo")
    assert index == len(before["aliases"])
    assert store.append_of(str(everything), "aliases", "todo") == index + 1
    assert store.clean_at(everything, "aliases")[-2:] == ["todo", "todo"]
    assert store.payload_at(everything)["aliases"] == [*before["aliases"], "todo"]
    store.replace_at(everything, before)
    assert store.payload_at(everything) == before


def test_remove_field_at_returns_the_value_it_took(world: World):
    world.store.update_field_at(CLIENT, "notes", "alergia al maní")
    assert world.store.remove_field_at(CLIENT, "notes") == "alergia al maní"
    assert world.store.payload_at(CLIENT)["notes"] == ""


def test_matches_at_is_sldbs_where_over_the_document_or_a_payload(world: World):
    store = world.store
    capacity = store.payload_at(TABLE)["capacity"]
    assert store.matches_at(TABLE, f"capacity = {capacity}")
    assert store.matches_of("Table:table-3", f"capacity = {capacity}")
    unsaved = dict(store.payload_at(TABLE), capacity=capacity + 40)
    assert store.matches_at(TABLE, f"capacity = {capacity + 40}", unsaved)
    assert not store.matches_at(TABLE, f"capacity = {capacity + 40}")
    with pytest.raises(StoreError, match="no Table named"):
        store.matches_at(DocId.parse("Table:table-999"), "capacity > 0")


NEW = DocId.parse("Table:table-77")


def test_create_at_returns_the_id_and_refuses_a_second_one(world: World):
    store, path = world.store, world.root / "tables" / "t77.md"
    payload = dict(store.payload_at(TABLE), number=77)
    assert store.create_at(NEW, payload, path) == NEW
    with pytest.raises(StoreError, match="a Table named 'table-77' already exists"):
        store.create_at(NEW, payload, path)


def test_untrack_at_and_track_at_take_the_document_out_and_back(world: World):
    store = world.store
    path = store.path_at(NEW)
    store.untrack_at(NEW)
    assert store.doc_at(NEW) is None
    store.track_at(NEW, path)
    assert store.payload_at(NEW)["number"] == 77
