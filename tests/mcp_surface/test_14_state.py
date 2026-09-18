"""spec 14 §2.3: the state of a world — its schema, its recent ledger, its integrity and the
legal transitions out of a state."""

from __future__ import annotations

import pytest

from mcp_surface.mounted import mount
from worlds.restaurant import build_restaurant

RESERVATION = "Reservation:reservation-2026-09-11-luis-soto"


def test_the_schema_has_the_projection_models_and_every_relation_type(get):
    answer = get("kb://rest/_schema")
    assert [m["name"] for m in answer["models"]] == [
        "Client",
        "Table",
        "Reservation",
        "State",
    ]
    zone = next(f for m in answer["models"] for f in m["fields"] if f["name"] == "zone")
    assert zone["enum"] == ["terrace", "indoor"]
    assigned = next(r for r in answer["relation_types"] if r["name"] == "assigned_to")
    assert assigned["condition"] == "capacity >= {party_size}"
    assert assigned["source_types"] == ["Reservation"]


def test_integrity_is_what_pron_check_and_the_edge_index_say(get):
    answer = get("kb://rest/_store/integrity")
    assert answer["ok"] is True
    assert answer["lints"] == [] and answer["edges"] == {"errors": [], "stale": []}


def test_transitions_from_a_state_with_their_conditions(get):
    answer = get("kb://rest/_transitions/Reservation/pending")
    to = {t["to"]: t["condition"] for t in answer["transitions"]}
    assert to == {"confirmed": "party_size <= 8", "cancelled": ""}
    assert answer["transitions"][0]["state"]["uri"].startswith("kb://rest/State/")
    assert get("kb://rest/_transitions/Reservation/seated")["notes"]


def test_an_unknown_state_address_is_an_error(get):
    with pytest.raises(LookupError, match="no state address"):
        get("kb://rest/_nothing")


def test_the_ledger_lists_the_last_moves_newest_first(tmp_path):
    world = build_restaurant(tmp_path)
    app = mount(world)
    assert app.tools.call("kb_get", uri="kb://rest/_ledger/recent")["moves"] == []
    session = app.mounts.session("rest", "agent-7")
    session.eval(f'(change (doc "{RESERVATION}") notes "window seat")')
    [move] = app.tools.call("kb_get", uri="kb://rest/_ledger/recent")["moves"]
    assert move["speaker"] == "agent-7" and move["outcome"] == "unico"
    assert move["writes"] and move["hash_before"]
    assert move["uri"] == f"kb://rest/MoveDoc/{move['id']}"
