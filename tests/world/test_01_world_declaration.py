"""Step 1: a world is a store. pron opens it and reads its declaration from its documents."""

from __future__ import annotations

from sldb.cli import main as sldb_main

from pron.world.doc_id import DocId
from pron.world.world import World


def test_store_passes_integrity_and_lists_exactly_the_declared_models(world: World):
    check = ["stores", "check", "--store", str(world.store.sp)]
    assert sldb_main([*check, "--pythonpath", world.store.pythonpath]) == 0
    assert set(world.model_names()) == {
        "Client",
        "Table",
        "Reservation",
        "State",
        "RelationTypeDoc",
        "RelationDoc",
        "AnchorDoc",
        "ProjectionDoc",
        "MoveDoc",
        "TheoremDoc",
    }


def test_declaration_is_read_from_documents(world: World):
    rts = world.relation_types()
    assert rts["assigned_to"]["condition"] == "capacity >= {party_size}"
    assert rts["assigned_to"]["target_types"] == ["Table"]
    proj = world.projection("all")
    assert proj["key"] == {"Table": "number"}
    assert {r["name"]: r["mode"] for r in proj["relations"]}["transitions_to"] == "read"


def test_schema_and_family_come_from_the_store(world: World):
    fields = {f["name"]: f for f in world.store.schema("Reservation")}
    assert fields["status"]["kind"] == "enum" and fields["status"]["enum"] == [
        "pending",
        "confirmed",
        "seated",
        "cancelled",
    ]
    assert fields["party_size"]["description"] == "Number of people coming."
    assert world.family_of("Reservation") == ["Reservation"]


def test_addresses_and_fields_read_by_address(world: World):
    assert world.store.get("st.{Table}.table-12.capacity") == 6
    assert sorted(world.store.find("st.{Table}", 'zone = "terrace"')) == [
        "st.{Table}.table-12",
        "st.{Table}.table-14",
        "st.{Table}.table-20",
    ]
    assert world.store.hash_c(DocId.of("Table", "table-12"))
