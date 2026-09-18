"""Level-2 write tools (spec 14 §4, §5): relation types are writable models only from level
2, and an edit of one is simulated against the edges of its type before it writes."""

from __future__ import annotations

from conftest import LUIS, session

from pron.mcp.writes import RuleEffect, Writes
from pron.world.doc_id import DocId
from pron.world.world import World

RT = "RelationTypeDoc:rt-assigned_to"


def _condition(world: World) -> str:
    return world.store.payload(DocId.parse(RT))["condition"]


def test_below_level_2_relation_types_do_not_exist(world: World):
    s = session(world)
    r = s.eval(f'(change (doc "{RT}") condition "")')
    assert r.outcome == "missing", r.text
    r = Writes(s).rule_edit("assigned_to", {"condition": ""})
    assert r["outcome"] == "error" and r["level"] == {"needed": 2, "session": 1}


def test_an_edit_that_breaks_edges_is_held(world: World):
    w = Writes(session(world, "rules"))
    r = w.rule_edit("assigned_to", {"condition": "capacity >= 100"})
    assert r["outcome"] == "error" and not r["writes"]
    (broken,) = r["broken"]
    assert broken["source"] == LUIS and "capacity >= 100" in broken["reasons"][0]
    assert _condition(world) == "capacity >= {party_size}"


def test_confirm_writes_it_anyway_and_undo_puts_it_back(world: World):
    w = Writes(session(world, "rules"))
    r = w.rule_edit("assigned_to", {"condition": "capacity >= 100"}, confirm=True)
    assert r["outcome"] == "unico" and r["move_id"] and len(r["broken"]) == 1, r
    assert _condition(world) == "capacity >= 100"
    assert w.undo()["outcome"] == "unico"
    assert _condition(world) == "capacity >= {party_size}"


def test_an_edit_that_breaks_nothing_writes(world: World):
    w = Writes(session(world, "rules"))
    r = w.rule_edit("assigned_to", {"description": "Where they sit."})
    assert r["outcome"] == "unico" and r["broken"] == [], r


def test_types_and_cardinality_are_simulated(world: World):
    s = session(world, "rules")
    effect = RuleEffect(s)
    (by_type,) = effect("assigned_to", {"target_types": ["Client"]})
    assert "target Table:table-3" in by_type["reasons"][0]
    s.eval(
        '(create Reservation (as "r-2") (date "2026-09-12") (time "21:00") (party_size 2) (status "pending") (notes ""))'
    )
    s.eval('(assert assigned_to (doc "Reservation:r-2") (doc "Table:table-3"))')
    broken = effect("assigned_to", {"cardinality": "one_to_one"})
    assert len(broken) == 2 and all(
        "several sources" in b["reasons"][0] for b in broken
    )


def test_a_relation_type_is_declared_as_a_document(world: World):
    w = Writes(session(world, "rules"))
    r = w.rule_declare(
        "likes",
        ["Client"],
        ["Table"],
        "many_to_many",
        "A favourite table.",
        axis="WHAT",
    )
    assert r["outcome"] == "unico", r["text"]
    payload = world.store.payload(DocId.parse("RelationTypeDoc:rt-likes"))
    assert payload["target_types"] == ["Table"] and payload["axis"] == "WHAT"
    assert w.rule_declare("x", [], [], "many", "")["outcome"] == "error"
