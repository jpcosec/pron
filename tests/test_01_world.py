"""Step 1: a world is a store. pron opens it, reads its declaration, refreshes its graph."""

from __future__ import annotations

from pathlib import Path

import pytest

from sldb.cli import main as sldb_main

from pron.world import World
from worlds.restaurant import build_restaurant


@pytest.fixture(scope="module")
def world(tmp_path_factory) -> World:
    return build_restaurant(tmp_path_factory.mktemp("restaurant"))


def test_store_passes_integrity_and_lists_exactly_the_declared_models(world: World):
    assert (
        sldb_main(
            [
                "stores",
                "check",
                "--store",
                str(world.store.sp),
                "--pythonpath",
                world.store.pythonpath,
            ]
        )
        == 0
    )
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
    assert world.store.hash_c("Table", "table-12")


def test_alias_with_steps_round_trips(world: World):
    d = world.store.doc("AnchorDoc", "anchor-book")
    assert d.payload["ref"] == "compose"
    assert d.payload["steps"][1] == {
        "do": "assert",
        "relation": "booked_by",
        "source": "$created",
        "target": "$referent:Client",
    }
    assert "book her" in d.payload["forms"]


def test_graph_is_built_fresh_and_typed(world: World):
    assert world.graph.available() and world.graph_is_fresh()
    edges = world.graph.edges_from(
        "sldb://document/Reservation:reservation-2026-09-11-luis-soto"
    )
    rels = {e["relation"]: e for e in edges}
    assert rels["assigned_to"]["target"] == "sldb://document/Table:table-3"
    assert rels["assigned_to"]["metadata"]["condition"] == "capacity >= {party_size}"
    verbs = {e["relation"] for e in world.graph.edges_to("sldb://model/Reservation")}
    assert {"applies_to_source", "names"} <= verbs


def test_hash_mundo_ignores_the_ledger_but_sees_a_schema_change(world: World):
    before = world.hash_mundo()
    world.store.create(
        "MoveDoc",
        "move-test-1",
        {
            "id": "move-test-1",
            "at": "2026-09-09T00:00:00Z",
            "speaker": "",
            "outcome": "unico",
            "state_before": "libre",
            "state_after": "libre",
            "hash_before": before,
            "hash_after": before,
            "refers_to": "",
            "sentence": "x",
            "record": {"a": 1},
        },
        world.root / "ledger" / "move-test-1.md",
    )
    assert world.hash_mundo() == before
    assert world.graph_is_fresh()
    world.store.update_field("Table", "table-20", "capacity", 3)
    assert world.hash_mundo() != before
    assert not world.graph_is_fresh()
    world.refresh()
    assert world.graph_is_fresh()


def test_create_with_relative_path_lands_under_the_world_root(
    world: World, tmp_path, monkeypatch
):
    """A relative path is relative to the world, not to the process cwd: sldb records paths
    relative to the root, so a cwd-relative file would be tracked as missing."""
    monkeypatch.chdir(tmp_path)
    world.store.create(
        "Client",
        "client-rel",
        {"name": "Rel", "phone": "1", "notes": ""},
        Path("clients") / "rel.md",
    )
    assert (world.root / "clients" / "rel.md").exists()
    assert not (tmp_path / "clients").exists()
    assert world.store.doc("Client", "client-rel") is not None
    assert (
        world.store.doc_path("Client", "client-rel")
        == world.root / "clients" / "rel.md"
    )
