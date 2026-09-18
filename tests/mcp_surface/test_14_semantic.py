"""spec 14 §2.2: semantic addresses resolve to sets, from what the world declares — tags,
enumerated values, families, relations — composed with & and restricted by a model."""

from __future__ import annotations

from mcp_surface.mounted import ids

TERRACE = ["Table:table-12", "Table:table-14", "Table:table-20"]
RESERVATION = "Reservation:reservation-2026-09-11-luis-soto"


def test_an_enumerated_value_names_the_documents_that_hold_it(get):
    answer = get("kb://rest/@terrace")
    assert ids(answer) == TERRACE
    assert answer["documents"][0]["via"] == ["enum:Table.zone"]
    assert answer["documents"][0]["uri"] == "kb://rest/Table/table-12"


def test_a_tag_names_the_documents_tagged_with_it(get):
    answer = get("kb://rest/@type.restaurant.client")
    assert ids(answer) == ["Client:client-ana-perez", "Client:client-luis-soto"]
    assert {d["via"][0] for d in answer["documents"]} == {"tag"}


def test_what_the_world_does_not_declare_is_empty_and_says_so(get):
    answer = get("kb://rest/@why")
    assert answer["documents"] == [] and "@why" in answer["notes"][0]
    walk = get(f"kb://rest/@{RESERVATION}/likes")
    assert walk["documents"] == [] and "'likes' is not declared" in walk["notes"][0]


def test_a_model_restricts_the_set_to_its_family(get):
    assert ids(get("kb://rest/Table/@terrace")) == TERRACE
    assert ids(get("kb://rest/Client/@terrace")) == []
    assert ids(get("kb://rest/Reservation/@pending")) == [RESERVATION]


def test_a_family_names_the_models_that_declare_it(get):
    assert len(ids(get("kb://rest/@family/restaurant"))) == 12
    assert ids(get("kb://rest/@family/table")) == sorted(ids(get("kb://rest/Table")))
    assert get("kb://rest/@family/kitchen")["notes"]


def test_a_relation_walks_forward_and_backwards(get):
    assert ids(get(f"kb://rest/@{RESERVATION}/booked_by")) == [
        "Client:client-luis-soto"
    ]
    assert ids(get("kb://rest/@Client:client-luis-soto/~booked_by")) == [RESERVATION]


def test_walks_chain_and_a_bare_name_starts_them(get):
    answer = get("kb://rest/@client-luis-soto/~booked_by/assigned_to")
    assert ids(answer) == ["Table:table-3"]
    assert answer["documents"][0]["via"] == ["walk:~booked_by/assigned_to"]


def test_ampersand_intersects_and_keeps_every_source(get):
    answer = get("kb://rest/@terrace&@type.restaurant.table")
    assert ids(answer) == TERRACE
    assert answer["documents"][0]["via"] == ["enum:Table.zone", "tag"]
    assert ids(get("kb://rest/@terrace&@indoor")) == []


def test_ranked_search_returns_addresses_with_scores_and_its_method(get):
    answer = get("kb://rest/?Luis")
    assert answer["method"] == "difflib"
    assert answer["documents"][0]["id"] == "Client:client-luis-soto"
    assert answer["documents"][0]["score"] == 1.0
    assert (
        get("kb://rest/%3FLuis")["documents"][0]["uri"]
        == "kb://rest/Client/client-luis-soto"
    )
