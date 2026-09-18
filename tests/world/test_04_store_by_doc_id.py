"""The store read and written by `DocId` (spec 02, 04): every operation on one document
takes the id as a value, never a model, a name and a store apart."""

from __future__ import annotations

import pytest

from pron.world.doc_id import DocId
from pron.world.store_error import StoreError
from pron.world.world import World

TABLE = DocId.parse("Table:table-3")
CLIENT = DocId.parse("Client:client-ana-perez")


def _projection(world: World) -> DocId:
    return DocId.of("ProjectionDoc", world.store.docs_of("ProjectionDoc")[0].name)


def test_reads_name_the_document_by_its_id(world: World):
    store = world.store
    assert store.doc(TABLE) is store.doc(DocId.parse("local:Table:table-3"))
    assert store.doc(TABLE).name == "table-3"
    assert store.payload(TABLE)["number"] == 3
    assert store.hash_c(TABLE) != ""
    assert store.doc_path(TABLE).name.endswith(".md")


def test_a_document_that_is_not_there(world: World):
    nobody = DocId.parse("Table:table-999")
    assert world.store.doc(nobody) is None
    assert world.store.hash_c(nobody) == "" and world.store.doc_path(nobody) is None
    with pytest.raises(StoreError, match="no Table named 'table-999'$"):
        world.store.payload(nobody)
    with pytest.raises(StoreError, match="no store linked as 'Z'"):
        world.store.hash_c(nobody.in_store("Z"))


def test_field_writes_return_what_was_there(world: World):
    store = world.store
    capacity = store.payload(TABLE)["capacity"]
    assert store.update_field(TABLE, "capacity", capacity + 1) == capacity
    assert store.update_field(TABLE, "capacity", capacity) == capacity + 1
    assert store.payload(TABLE)["capacity"] == capacity


def test_list_writes_and_whole_payload_rewrite(world: World):
    store, everything = world.store, _projection(world)
    before = store.payload(everything)
    index = store.append(everything, "aliases", "todo")
    assert index == len(before["aliases"])
    assert store.append(everything, "aliases", "todo") == index + 1
    assert store.clean(everything, "aliases")[-2:] == ["todo", "todo"]
    assert store.payload(everything)["aliases"] == [*before["aliases"], "todo"]
    store.replace(everything, before)
    assert store.payload(everything) == before


def test_remove_field_returns_the_value_it_took(world: World):
    world.store.update_field(CLIENT, "notes", "alergia al maní")
    assert world.store.remove_field(CLIENT, "notes") == "alergia al maní"
    assert world.store.payload(CLIENT)["notes"] == ""


def test_matches_is_sldbs_where_over_the_document_or_a_payload(world: World):
    store = world.store
    capacity = store.payload(TABLE)["capacity"]
    assert store.matches(TABLE, f"capacity = {capacity}")
    unsaved = dict(store.payload(TABLE), capacity=capacity + 40)
    assert store.matches(TABLE, f"capacity = {capacity + 40}", unsaved)
    assert not store.matches(TABLE, f"capacity = {capacity + 40}")
    with pytest.raises(StoreError, match="no Table named"):
        store.matches(DocId.parse("Table:table-999"), "capacity > 0")


NEW = DocId.parse("Table:table-77")


def test_create_returns_the_id_and_refuses_a_second_one(world: World):
    store, path = world.store, world.root / "tables" / "t77.md"
    payload = dict(store.payload(TABLE), number=77)
    assert store.create(NEW, payload, path) == NEW
    with pytest.raises(StoreError, match="a Table named 'table-77' already exists"):
        store.create(NEW, payload, path)


def test_untrack_and_track_take_the_document_out_and_back(world: World):
    store = world.store
    path = store.doc_path(NEW)
    store.untrack(NEW)
    assert store.doc(NEW) is None
    store.track(NEW, path)
    assert store.payload(NEW)["number"] == 77
