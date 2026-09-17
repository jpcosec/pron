"""What the review of 2026-09-08 found missing against the spec, on reading and writing: the
second hash_mundo read before executing (11 §5), a complement that crosses edges, a read-only
session, and a write that would not validate."""

from __future__ import annotations


from pron.session import Session
from pron.sexpr.prevalidation.prevalidator import Prevalidator
from pron.world.world import World

NOW = "2026-09-09"


def _racing_prevalidator(world: World):
    """A Prevalidator whose first run finds the world changed under it."""
    original = Prevalidator.__call__
    calls = []

    def racing(self, parts, plans, ctx):
        if not calls:  # the first time through: the world changes between understanding and executing
            calls.append(1)
            world.store.create(
                "Table",
                "table-99",
                {"number": 99, "capacity": 2, "zone": "indoor"},
                world.root / "tables" / "99.md",
            )
        return original(self, parts, plans, ctx)

    return racing


def test_hash_mundo_is_read_again_before_executing(world: World, monkeypatch):
    s = Session(world, projection="all", speaker="jp", now=NOW)
    monkeypatch.setattr(Prevalidator, "__call__", _racing_prevalidator(s.world))
    r = s.turn("the large tables")
    assert r.outcome == "unico", r.text
    assert any("changed while understanding" in line for line in r.trace), r.trace


def _said(r) -> str:
    return r.text + " / " + " | ".join(r.trace)


def _reads_across_the_complement(s: Session) -> None:
    r = s.turn("the reservations of Luis Soto")
    assert r.outcome == "unico" and "20:00" in r.text, _said(r)
    assert any("booked_by" in q for q in r.trace), r.trace
    r = s.turn("Luis Soto's reservations for Friday")
    assert (
        r.outcome == "unico"
        and "20:00" in r.text
        and any('date = "2026-09-11"' in q for q in r.trace)
    ), _said(r)
    r = s.turn("Luis Soto's reservations for Saturday")
    assert r.outcome == "unico" and r.text == "None.", r.text
    r = s.turn("the tables of the reservations of Luis Soto")
    assert r.outcome == "unico" and r.text == "table 3.", _said(r)


def test_a_complement_names_a_related_document_and_crosses_its_edges(world: World):
    s = Session(world, projection="all", speaker="jp", now=NOW)
    _reads_across_the_complement(s)
    r = s.turn("confirm the reservation of Luis Soto")
    assert r.outcome == "unico" and "Done" in r.text, _said(r)
    assert (
        world.store.payload("Reservation", "reservation-2026-09-11-luis-soto")["status"]
        == "confirmed"
    )
    r = s.turn("the reservations of Nadie Nunca")
    assert r.outcome == "unico" and r.text == "None.", r.text


def test_a_read_only_session_writes_nothing_whatever_the_projection_allows(
    world: World,
):
    s = Session(world, projection="all", speaker="viewer", now=NOW, read_only=True)
    assert s.turn("the clients").outcome == "unico"
    r = s.turn("create a client named Zoe Lee, phone 1")
    assert (
        r.outcome == "missing" and world.store.doc("Client", "client-zoe-lee") is None
    ), r.text
    r = s.turn("confirm the reservation of Luis Soto")
    assert r.outcome == "missing", r.text
    assert all(
        not m["record"].get("writes")
        for m in (s.ledger.get(mid) for mid in [r.move_id])
    )


def test_removing_a_required_field_is_refused_not_raised(world: World):
    """A write whose payload would not validate is refused before anything is written
    (spec 11 §7), even when the model rejects it outright for a missing required field."""
    s = Session(world, projection="all", speaker="jp", now=NOW)
    assert s.turn("the tables on the terrace").outcome == "unico"
    r = s.turn("remove the zone of them")
    assert r.outcome == "error" and "zone" in r.text and "round-trip" in r.text
    assert not r.record["writes"]
    assert s.turn("the tables on the terrace").outcome == "unico"
