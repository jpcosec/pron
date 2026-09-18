"""Level-1 write tools (spec 14 §4): documents and edges written as forms in a session, each
leaving its MoveDoc and undone with `undo`; `dry_run` pre-validates and writes nothing."""

from __future__ import annotations

from conftest import LUIS, session

from pron.mcp.writes import EdgeIds, Writes
from pron.world.doc_id import DocId
from pron.world.world import World

EVA = "Client:client-eva"
EDGE = f"RelationDoc:assigned_to--{LUIS}--Table:table-3"


def _eva(w: Writes) -> dict:
    return w.doc_create(
        "Client", {"name": 'Eva "E"', "phone": "3", "notes": ""}, "client-eva"
    )


def test_a_document_is_created_edited_and_forgotten(world: World):
    w = Writes(session(world))
    r = _eva(w)
    assert r["outcome"] == "unico" and r["move_id"] and r["writes"][0]["done"]
    assert world.store.payload(DocId.parse(EVA))["name"] == 'Eva "E"'
    r = w.doc_edit(EVA, [{"op": "set", "field": "notes", "value": "window"}])
    assert r["outcome"] == "unico", r["text"]
    assert world.store.payload(DocId.parse(EVA))["notes"] == "window"
    assert w.doc_forget(EVA)["outcome"] == "unico"
    assert world.store.doc(DocId.parse(EVA)) is None


def test_a_dry_run_writes_nothing_and_leaves_no_move(world: World):
    s = session(world)
    files = sorted(world.root.rglob("*.md"))
    r = Writes(s).doc_edit(
        LUIS, [{"op": "set", "field": "party_size", "value": 5}], dry_run=True
    )
    assert r["outcome"] == "unico" and r["dry_run"] and not r["writes"], r
    assert world.store.payload(DocId.parse(LUIS))["party_size"] == 4
    assert sorted(world.root.rglob("*.md")) == files


def test_a_dry_run_says_what_prevalidation_refuses(world: World):
    r = Writes(session(world)).doc_edit(
        LUIS, [{"op": "set", "field": "status", "value": "seated"}], dry_run=True
    )
    assert r["outcome"] == "error" and "transition" in r["text"], r


def test_an_edge_is_expired_and_undone(world: World):
    s = session(world)
    w = Writes(s)
    assert EdgeIds(s)("assigned_to", LUIS, "Table:table-3") == EDGE
    r = w.edge_expire(LUIS, "assigned_to", "Table:table-3")
    assert r["outcome"] == "unico" and r["writes"][0]["address"] == EDGE, r
    assert s.verbs.targets_of(LUIS, "assigned_to") == []
    assert w.undo()["outcome"] == "unico"
    assert s.verbs.targets_of(LUIS, "assigned_to") == ["Table:table-3"]


def test_an_edge_is_asserted_through_its_checks(world: World):
    w = Writes(session(world))
    r = w.edge_assert(LUIS, "assigned_to", "Table:table-20")
    assert r["outcome"] == "error" and not r["writes"]
    w.edge_expire(LUIS, "assigned_to", "Table:table-3")
    r = w.edge_assert(LUIS, "assigned_to", "Table:table-12")
    assert r["outcome"] == "unico" and r["writes"][0]["done"], r


def test_an_edge_of_a_read_relation_is_not_negated(world: World):
    edge = "RelationDoc:transitions_to--State:state-reservation-pending--State:state-reservation-confirmed"
    r = session(world).eval(f'(forget (doc "{edge}"))')
    assert r.outcome == "error" and "cannot negate transitions_to" in r.text, r.text


def test_a_read_only_session_is_level_0(world: World):
    w = Writes(session(world, projection="rules", read_only=True))
    r = w.doc_forget(LUIS)
    assert w.level == 0 and r["outcome"] == "error" and r["level"]["needed"] == 1
    assert world.store.doc(DocId.parse(LUIS)) is not None
