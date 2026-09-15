"""Graph navigation and the document index: what a runtime reads from a world without
assembling anything of its own (spec 05, 10, 11 §2)."""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from pron.embedder import DocumentIndex, Matcher
from pron.graph import bare, doc_id, kind, tag_id
from pron.world import World
from worlds.restaurant import build_restaurant


@pytest.fixture(scope="module")
def world(tmp_path_factory) -> World:
    return build_restaurant(tmp_path_factory.mktemp("restaurant"))


# -- graph navigation -----------------------------------------------------------------------


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


# -- document index -------------------------------------------------------------------------


class CharBag:
    """A deterministic fake Embedder: normalized letter counts."""

    calls: list[list[str]] = []

    def id(self) -> str:
        return "charbag"

    def embed(self, texts):
        CharBag.calls.append(list(texts))
        out = []
        for t in texts:
            v = [0.0] * 26
            for c in t.lower():
                if "a" <= c <= "z":
                    v[ord(c) - 97] += 1
            n = math.sqrt(sum(x * x for x in v)) or 1.0
            out.append([x / n for x in v])
        return out


def test_index_embeds_only_what_changed_and_persists(tmp_path: Path):
    CharBag.calls = []
    idx = DocumentIndex(Matcher(CharBag()), tmp_path / "docs.json")
    stats = idx.index(
        [
            ("a", "h1", "terrace table"),
            ("b", "h2", "indoor room"),
            ("c", "h3", "phone number"),
        ]
    )
    assert stats == {"embedded": 3, "reused": 0, "dropped": 0}
    assert idx.index(
        [
            ("a", "h1", "terrace table"),
            ("b", "h2", "indoor room"),
            ("c", "h3", "phone number"),
        ]
    ) == {"embedded": 0, "reused": 3, "dropped": 0}
    stats = idx.index(
        [("a", "h1", "terrace table"), ("b", "h2-changed", "indoor room, renovated")]
    )
    assert stats == {"embedded": 1, "reused": 1, "dropped": 1}
    assert CharBag.calls[-1] == ["indoor room, renovated"]
    saved = json.loads((tmp_path / "docs.json").read_text())
    assert saved["embedder"] == "charbag" and set(saved["entries"]) == {"a", "b"}
    # a new instance reads the file back and needs no embedding
    again = DocumentIndex(Matcher(CharBag()), tmp_path / "docs.json")
    assert again.keys() == ["a", "b"]
    assert again.index([("a", "h1", "terrace table"), ("b", "h2-changed", "x")]) == {
        "embedded": 0,
        "reused": 2,
        "dropped": 0,
    }


def test_rank_orders_by_similarity_and_respects_k_and_threshold(tmp_path: Path):
    idx = DocumentIndex(Matcher(CharBag()), tmp_path / "docs.json")
    idx.index(
        [
            ("terrace", "1", "terrace table"),
            ("indoor", "2", "indoor room"),
            ("phone", "3", "phone number"),
        ]
    )
    ranked = idx.rank("terrace tables")
    assert [k for k, _ in ranked][0] == "terrace"
    assert all(ranked[i][1] >= ranked[i + 1][1] for i in range(len(ranked) - 1))
    assert len(idx.rank("terrace tables", k=1)) == 1
    top = ranked[0][1]
    assert idx.rank("terrace tables", threshold=top) == [("terrace", top)]


def test_a_cache_from_another_embedder_is_ignored(tmp_path: Path):
    path = tmp_path / "docs.json"
    DocumentIndex(Matcher(CharBag()), path).index([("a", "1", "x")])
    other = DocumentIndex(Matcher(), path)  # difflib
    assert other.keys() == []


def test_without_embedder_the_index_ranks_with_difflib(tmp_path: Path):
    idx = DocumentIndex(Matcher(), tmp_path / "docs.json")
    stats = idx.index(
        [("terrace", "1", "terrace table"), ("phone", "2", "phone number")]
    )
    assert stats["embedded"] == 2
    saved = json.loads((tmp_path / "docs.json").read_text())
    assert (
        saved["embedder"] == "difflib"
        and "vector" not in saved["entries"]["terrace"]
        and saved["entries"]["terrace"]["text"] == "terrace table"
    )
    assert idx.rank("terrace")[0][0] == "terrace"


# -- world ------------------------------------------------------------------------------------


def test_refresh_if_stale_only_refreshes_when_needed(world: World, tmp_path: Path):
    assert world.graph_is_fresh()
    assert world.refresh_if_stale() is False
    assert world.derived_dir == world.root / ".pron" and world.derived_dir.is_dir()
    world.store.create(
        "Client",
        "client-stale",
        {"name": "Stale", "phone": "0", "notes": ""},
        Path("clients") / "stale.md",
    )
    assert not world.graph_is_fresh()
    assert world.refresh_if_stale() is True
    assert world.graph_is_fresh() and world.graph.has_node(
        doc_id("Client:client-stale")
    )


def test_document_index_exposes_its_vectors(tmp_path):
    from pron.embedder import DocumentIndex, Matcher

    idx = DocumentIndex(Matcher(CharBag()), tmp_path / "docs.json")
    idx.index([("a", "h1", "alpha"), ("b", "h2", "beta")])
    vectors = idx.vectors()
    assert set(vectors) == {"a", "b"}
    assert all(isinstance(v, list) and v for v in vectors.values())
    bare = DocumentIndex(Matcher(None), tmp_path / "difflib.json")
    bare.index([("a", "h1", "alpha")])
    assert bare.vectors() == {}
