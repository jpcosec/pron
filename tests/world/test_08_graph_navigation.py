"""Graph navigation: what a runtime reads from a world's graph without assembling anything of
its own (spec 05, 10, 11 §2), and the graph kept fresh against the store."""

from __future__ import annotations

import shutil
from pathlib import Path

from pron.world.graph import bare, doc_id, kind, tag_id
from pron.world.world import World


def test_ids_round_trip():
    assert tag_id("type.restaurant") == "sldb://semantic_tag/type.restaurant"
    assert bare("sldb://document/Table:table-3") == "Table:table-3"
    assert bare("sldb://semantic_tag/type.restaurant.table") == "type.restaurant.table"
    assert bare("Table:table-3") == "Table:table-3"
    assert (
        kind("sldb://document/Table:table-3") == "document"
        and kind("Table:table-3") is None
    )


def test_nodes_of_type_are_documents_by_model(world: World):
    tables = world.graph.nodes_of_type("Table")
    assert tables == sorted(doc_id(f"Table:table-{n}") for n in (3, 5, 12, 14, 20))
    assert world.graph.node_type(tables[0]) == "Table"


def test_tag_children_parent_and_roots(world: World):
    g = world.graph
    assert tag_id("type.restaurant.table") in g.children(tag_id("type.restaurant"))
    assert g.parent(tag_id("type.restaurant.table")) == tag_id("type.restaurant")
    roots = g.roots("semantic_tag", "semantic_parent")
    assert tag_id("type") in roots and tag_id("type.restaurant") not in roots


def test_descendants_walk_the_dag_breadth_first(world: World):
    g = world.graph
    all_under_type = g.descendants(tag_id("type"))
    assert (
        tag_id("type.restaurant") in all_under_type
        and tag_id("type.restaurant.table") in all_under_type
    )
    assert tag_id("type.restaurant.table") not in g.descendants(tag_id("type"), depth=1)
    assert tag_id("type") not in all_under_type


# Tags every document of a store carries (sldb's StructuredNLDoc can declare representation and
# source axes for all models): shared by everything, so a caller skips them by prefix.
STORE_WIDE = ("representation.", "source.")


def test_documents_tagged_alike_are_neighbors(world: World):
    g = world.graph
    table3 = doc_id("Table:table-3")
    siblings = g.neighbors_via(table3, "tagged_as", exclude_prefixes=STORE_WIDE)
    assert table3 not in siblings
    assert siblings == sorted(doc_id(f"Table:table-{n}") for n in (5, 12, 14, 20))
    assert doc_id("Client:client-ana-perez") not in siblings  # a different leaf tag
    # the shared target can be excluded by prefix without pron knowing what the tag means
    assert (
        g.neighbors_via(table3, "tagged_as", exclude_prefixes=("type.", *STORE_WIDE))
        == []
    )
    # the model node and the sections carry the same tag; they come back only on request
    everything = g.neighbors_via(table3, "tagged_as", same_kind=False)
    assert "sldb://model/Table" in everything and set(siblings) < set(everything)


def test_transitions_are_a_walk_too(world: World):
    g = world.graph
    pending = doc_id("State:state-reservation-pending")
    assert g.targets(pending, "transitions_to") == sorted(
        [
            doc_id("State:state-reservation-cancelled"),
            doc_id("State:state-reservation-confirmed"),
        ]
    )
    assert g.roots("State", "transitions_to") == sorted(
        [
            doc_id("State:state-reservation-cancelled"),
            doc_id("State:state-reservation-seated"),
        ]
    )
    assert g.descendants(
        doc_id("State:state-reservation-seated"), "transitions_to"
    ) == [
        doc_id("State:state-reservation-confirmed"),
        doc_id("State:state-reservation-pending"),
    ]
    # sources: who can move into confirmed
    assert g.sources(doc_id("State:state-reservation-confirmed"), "transitions_to") == [
        pending
    ]


# -- world ------------------------------------------------------------------------------------


def test_a_pron_write_keeps_the_graph_fresh_without_a_refresh(world: World):
    """Every write goes through sldb's own API, which resyncs the edge shard it touches in
    the same operation (spec 11 §5): pron never needs an explicit refresh to see it."""
    assert world.graph_is_fresh()
    assert world.refresh_if_stale() is False
    world.store.create(
        "Client",
        "client-stale",
        {"name": "Stale", "phone": "0", "notes": ""},
        Path("clients") / "stale.md",
    )
    assert world.graph_is_fresh()
    assert world.graph.has_node(doc_id("Client:client-stale"))
    assert world.refresh_if_stale() is False


def test_refresh_if_stale_catches_a_shard_lost_outside_sldb(world: World):
    """`stale` names documents whose shard is missing or built from another hash_c: the one
    case a write outside sldb's own API (or by-hand tampering) can leave behind."""
    assert world.graph_is_fresh()
    assert world.derived_dir == world.root / ".pron" and world.derived_dir.is_dir()
    shutil.rmtree(world.store.sp / "runtime" / "edges")
    assert not world.graph_is_fresh()
    assert world.refresh_if_stale() is True
    assert world.graph_is_fresh() and world.graph.has_node(doc_id("Table:table-3"))
