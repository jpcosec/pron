"""The port and the overlay: reads see what a plan would leave, the world never moves."""

from __future__ import annotations

import pytest

from plnr import MemoryWorld, Overlay, World, payload_matches


def test_memory_world_satisfies_the_port(world):
    assert isinstance(world, World)


def test_predicates_cover_what_a_noun_phrase_asks():
    payload = {"capacity": 6, "zone": "terrace", "note": "", "tags": ["a"]}
    assert payload_matches(payload, "capacity >= 6")
    assert not payload_matches(payload, "capacity > 6")
    assert payload_matches(payload, 'zone = "terrace"')
    assert payload_matches(payload, "zone ~ terr")
    assert payload_matches(payload, "has(tags)")
    assert not payload_matches(payload, "has(note)")
    assert not payload_matches(payload, "has(missing)")
    assert payload_matches(payload, "")


def test_an_absent_field_matches_neither_equality_nor_inequality():
    assert not payload_matches({}, 'zone = "terrace"')
    assert not payload_matches({}, 'zone != "terrace"')


def test_a_predicate_that_does_not_parse_is_an_error_not_an_empty_answer():
    with pytest.raises(ValueError):
        payload_matches({"a": 1}, "this is not a predicate")


def test_overlay_reads_its_pending_documents(world):
    overlay = Overlay(world)
    overlay.create("r-2", "Reservation")
    overlay.set_field("r-2", "party_size", 6)
    assert overlay.model_of("r-2") == "Reservation"
    assert overlay.payload("r-2") == {"party_size": 6}
    assert "r-2" in set(overlay.docs("Reservation"))
    assert overlay.matches("r-2", "party_size >= 6")


def test_overlay_shadows_a_field_without_touching_the_world(world):
    overlay = Overlay(world)
    overlay.set_field("r-1", "status", "confirmed")
    assert overlay.payload("r-1")["status"] == "confirmed"
    assert world.payload("r-1")["status"] == "pending"
    assert overlay.matches("r-1", 'status = "confirmed"')
    assert not world.matches("r-1", 'status = "confirmed"')


def test_overlay_edges_add_to_the_world_ones(world):
    overlay = Overlay(world)
    overlay.link("assigned_to", "r-2", "t12")
    assert ("assigned_to", "r-2", "t12") in set(overlay.edges("assigned_to"))
    assert ("assigned_to", "r-1", "t10") in set(overlay.edges("assigned_to"))
    assert ("assigned_to", "r-2", "t12") not in set(world.edges())


def test_the_log_is_what_a_committer_would_replay(world):
    overlay = Overlay(world)
    overlay.create("r-2", "Reservation")
    overlay.link("booked_by", "r-2", "ana")
    assert overlay.wrote()
    assert overlay.log == [
        ["create", "Reservation", "r-2"],
        ["assert", "booked_by", "r-2", "ana"],
    ]


def test_overlays_nest(world):
    outer = Overlay(world)
    outer.set_field("r-1", "status", "confirmed")
    inner = Overlay(outer)
    inner.set_field("r-1", "status", "seated")
    assert inner.payload("r-1")["status"] == "seated"
    assert outer.payload("r-1")["status"] == "confirmed"
    assert world.payload("r-1")["status"] == "pending"


def test_a_world_can_be_built_empty():
    empty = MemoryWorld()
    assert list(empty.docs()) == []
    assert list(empty.edges()) == []
