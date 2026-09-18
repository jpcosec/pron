"""spec 14 §3: the read tools over the read plane, and the tool table the server registers
from — one `add` per tool, every call through the gate (spec 14 §5)."""

from __future__ import annotations

import pytest

from mcp_surface.mounted import ids
from pron.mcp.read_tools import NAMES
from pron.mcp.tool_table import ToolTable

RESERVATION = "Reservation:reservation-2026-09-11-luis-soto"


def test_find_intersects_predicates(app):
    both = app.tools.call(
        "kb_find",
        world="rest",
        model="Table",
        where=["capacity >= 6", 'zone = "terrace"'],
    )
    assert ids(both) == ["Table:table-12", "Table:table-14"]
    assert both["documents"][0]["uri"] == "kb://rest/Table/table-12"
    assert (
        len(ids(app.tools.call("kb_find", world="rest", model="Table", limit=2))) == 2
    )


def test_find_with_text_ranks_among_the_matches(app):
    answer = app.tools.call(
        "kb_find",
        world="rest",
        model="Table",
        where=["capacity >= 6"],
        text="number 14",
    )
    assert answer["method"] == "difflib"
    assert set(ids(answer)) == {"Table:table-12", "Table:table-14"}


def test_find_refuses_a_bad_predicate_and_a_model_outside_the_projection(app):
    with pytest.raises(Exception):
        app.tools.call("kb_find", world="rest", model="Table", where=["capacity >>> 6"])
    with pytest.raises(LookupError):
        app.tools.call("kb_find", world="rest", model="AnchorDoc")


def test_read_is_the_whole_document(app):
    answer = app.tools.call("kb_read", world="rest", id="Table:table-3")
    assert (
        answer["payload"]["capacity"] == 4
        and answer["uri"] == "kb://rest/Table/table-3"
    )


def test_neighbors_carry_origin_condition_and_the_other_address(app):
    answer = app.tools.call(
        "kb_neighbors", world="rest", id=RESERVATION, relation="assigned_to"
    )
    [edge] = answer["edges"]
    assert (
        edge["origin"] == "relation_doc"
        and edge["condition"] == "capacity >= {party_size}"
    )
    assert edge["other"]["uri"] == "kb://rest/Table/table-3"
    back = app.tools.call(
        "kb_neighbors",
        world="rest",
        id="Client:client-luis-soto",
        direction="in",
        relation="booked_by",
    )
    assert [e["other"]["id"] for e in back["edges"]] == [RESERVATION]
    with pytest.raises(ValueError):
        app.tools.call("kb_neighbors", world="rest", id=RESERVATION, direction="up")


def test_the_read_tools_are_in_the_table_at_level_zero(app):
    assert [s.name for s in app.tools] == list(NAMES)
    assert {s.level for s in app.tools} == {0}
    assert "kb://" in app.tools["kb_get"].description


def test_a_new_tool_is_one_add_and_the_gate_sees_every_call():
    table = ToolTable()

    def kb_echo(world: str, value: int = 1) -> dict:
        """Echo."""
        return {"world": world, "value": value}

    table.add("kb_echo", kb_echo, level=1)
    assert table.call("kb_echo", world="w") == {"world": "w", "value": 1}
    table.gate = lambda spec, args: {"outcome": "error", "needs": spec.level}
    assert table.call("kb_echo", world="w") == {"outcome": "error", "needs": 1}
    with pytest.raises(ValueError, match="already"):
        table.add("kb_echo", kb_echo)
