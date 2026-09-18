"""spec 14 §4, §5: the write tools in the table the server registers from, and the ladder at
its door — a tool above the session's level answers the ladder's error and does not run."""

from __future__ import annotations

from mcp_wiring.wired import LUIS, restaurant, wire
from pron.mcp.read_tools import NAMES as READS

WRITES = ["kb_doc_create", "kb_doc_edit", "kb_doc_forget", "kb_edge_assert"]
LEVEL_1 = [*WRITES, "kb_edge_expire", "kb_undo"]


def test_the_table_holds_every_tool_with_its_level(tmp_path):
    app, _ = wire(restaurant(tmp_path))
    levels = {spec.name: spec.level for spec in app.tools}
    assert list(levels)[: len(READS)] == list(READS) and levels["kb_audit"] == 0
    assert all(levels[t] == 1 for t in LEVEL_1)
    assert levels["kb_rule_declare"] == levels["kb_rule_edit"] == 2
    assert levels["kb_model_create"] == levels["kb_model_extend"] == 3


def test_reads_pass_without_opening_a_session(tmp_path):
    app, w = wire(restaurant(tmp_path), "reader")
    assert (
        app.tools.call("kb_read", world=w, id="Table:table-3")["payload"]["number"] == 3
    )
    assert app.mounts._sessions == {}


def test_a_level_0_projection_refuses_content(tmp_path):
    app, w = wire(restaurant(tmp_path), "reader")
    answer = app.tools.call("kb_doc_forget", world=w, id="Table:table-3")
    assert answer["outcome"] == "error" and answer["level"] == {
        "needed": 1,
        "session": 0,
    }
    assert (
        app.tools.call("kb_read", world=w, id="Table:table-3")["id"] == "Table:table-3"
    )


def test_level_1_refuses_rules_and_models_and_says_what_it_needs(tmp_path):
    app, w = wire(restaurant(tmp_path))
    rule = app.tools.call("kb_rule_edit", world=w, name="booked_by", changes={})
    model = app.tools.call("kb_model_create", world=w, name="Dish", fields=[])
    assert rule["level"] == {"needed": 2, "session": 1} and rule["writes"] == []
    assert model["level"] == {"needed": 3, "session": 1}


def test_a_write_goes_to_the_session_of_its_speaker(tmp_path):
    app, w = wire(restaurant(tmp_path))
    args = dict(world=w, source=LUIS, relation="assigned_to", target="Table:table-3")
    dry = app.tools.call("kb_edge_expire", **args, dry_run=True)
    assert dry["outcome"] == "unico" and dry["dry_run"] and dry["move_id"] == ""
    done = app.tools.call("kb_edge_expire", **args, speaker="agent-7")
    assert done["outcome"] == "unico" and done["move_id"]
    [move] = app.tools.call("kb_get", uri=f"kb://{w}/_ledger/recent")["moves"]
    assert move["speaker"] == "agent-7"
    assert set(app.mounts._sessions) == {(w, "mcp"), (w, "agent-7")}


def test_level_2_writes_rules(tmp_path):
    app, w = wire(restaurant(tmp_path), "rules")
    answer = app.tools.call(
        "kb_rule_declare",
        world=w,
        name="prefers",
        source_types=["Client"],
        target_types=["Table"],
        cardinality="many_to_many",
        description="A client's favourite tables.",
    )
    assert answer["outcome"] == "unico", answer["text"]
    assert answer["writes"][0]["address"] == "RelationTypeDoc:rt-prefers"
