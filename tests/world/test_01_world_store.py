"""Step 1: pron refreshes a world's graph, tells a schema change from a ledger entry, and
writes documents where the world keeps them."""

from __future__ import annotations

from pathlib import Path

from pron.world.world import World
from worlds.restaurant import build_restaurant


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


def test_update_index_says_on_stderr_what_it_skipped(tmp_path, capsys):
    """sldb's library API prints nothing: an update is silent on stdout, and only what it
    had to skip (a tracked file gone) is said, on stderr."""
    world = build_restaurant(tmp_path / "restaurant")
    missing = world.store.doc_path("Table", "table-3")
    missing.unlink()
    capsys.readouterr()
    report = world.store.update_index()
    out = capsys.readouterr()
    assert report.skipped_documents and out.out == ""
    assert "Skipped missing documents:" in out.err
