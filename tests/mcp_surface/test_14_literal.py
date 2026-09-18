"""spec 14 §2.1: literal addresses — a model, a document, a field, an item — each a single
destination, every document with its own address; a model outside the projection does not
resolve (spec 01)."""

from __future__ import annotations

import pytest

from mcp_surface.mounted import ids
from pron.mcp.mount import Mount


def test_a_model_lists_its_documents_with_their_addresses(get):
    answer = get("kb://rest/Table")
    assert ids(answer)[:2] == ["Table:table-3", "Table:table-5"]
    assert answer["documents"][0]["uri"] == "kb://rest/Table/table-3"


def test_a_document_is_its_whole_payload(get):
    answer = get("kb://rest/Client/client-ana-perez")
    assert answer["payload"] == {
        "name": "Ana Pérez",
        "phone": "9 1111 0000",
        "notes": "",
    }
    assert answer["title"] == "Ana Pérez" and answer["id"] == "Client:client-ana-perez"


def test_a_field_is_its_value(get):
    answer = get("kb://rest/Table/table-14/capacity")
    assert answer["value"] == 8 and answer["uri"] == "kb://rest/Table/table-14/capacity"


@pytest.fixture
def wider(monkeypatch):
    """The restaurant's projection plus ProjectionDoc, whose fields are lists."""
    names = ["Client", "Table", "Reservation", "State", "ProjectionDoc"]
    monkeypatch.setattr(Mount, "models", lambda self: names)


def test_an_item_of_a_list_field(get, wider):
    answer = get("kb://rest/ProjectionDoc/projection-all/models/1")
    assert answer["value"] == "Table"


def test_an_item_needs_a_list_and_an_index_it_has(get, wider):
    with pytest.raises(LookupError, match="not a list"):
        get("kb://rest/Table/table-3/zone/0")
    with pytest.raises(LookupError, match="no item"):
        get("kb://rest/ProjectionDoc/projection-all/models/99")


def test_a_model_outside_the_projection_does_not_resolve(get):
    with pytest.raises(LookupError, match="not in projection"):
        get("kb://rest/RelationTypeDoc")
    with pytest.raises(LookupError, match="not in projection"):
        get("kb://rest/MoveDoc/move-1")


def test_an_unknown_field_or_document_is_an_error(get):
    with pytest.raises(LookupError, match="no field"):
        get("kb://rest/Table/table-3/colour")
    with pytest.raises(Exception, match="no Table named"):
        get("kb://rest/Table/table-99")


def test_the_world_alone_is_its_summary_and_bad_uris_are_refused(get):
    assert get("kb://rest")["world"]["name"] == "rest"
    with pytest.raises(ValueError, match="kb://"):
        get("http://rest/Table")
