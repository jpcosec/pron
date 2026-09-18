"""A goal that writes (spec 04, 13): searched over an overlay, committed by the kernel verbs.

The rules do the work — a book is a theorem of the world, not a construction of the surface —
and what comes out is an ordinary move: writes with their previous values, one refresh, one
MoveDoc. Order matters in this file: it is one conversation over one world.
"""

from __future__ import annotations

from pron.session import Session
from pron.world.doc_id import DocId

RESERVATION = "reservation-plnr-1"
BOOK = (
    "(goal (book Client:client-ana-perez Table:table-12 "
    f"Reservation:{RESERVATION} 2026-09-20 21:00 6))"
)


def test_a_goal_that_holds_creates_the_document_it_promised(session: Session):
    r = session.eval(BOOK)
    assert r.outcome == "unico", r.text
    assert r.text == "Done (8 writes).", r.text
    doc = session.world.store.doc(DocId.of("Reservation", RESERVATION))
    assert doc is not None
    assert doc.payload["party_size"] == 6
    assert doc.payload["status"] == "pending"
    assert doc.payload["date"] == "2026-09-20"


def test_the_edges_of_the_plan_are_asserted(session: Session):
    """The graph also carries the edges kgdb derives; the plan's own two are among them."""
    edges = session.verbs.edges_from(f"Reservation:{RESERVATION}")
    written = {(e["relation"], e["target"]) for e in edges.edges}
    assert ("booked_by", "Client:client-ana-perez") in written
    assert ("assigned_to", "Table:table-12") in written
    assert all(
        e["metadata"]["origin"] == "relation_doc"
        for e in edges.edges
        if e["relation"] in ("booked_by", "assigned_to")
    )


def test_an_antecedent_rule_fires_on_what_the_plan_asserted(session: Session):
    """note-the-booking is a THANTE: what follows because assigned_to was asserted."""
    doc = session.world.store.doc(DocId.of("Reservation", RESERVATION))
    assert doc.payload["notes"] == "assigned by a goal"


def test_the_move_keeps_the_writes_and_the_plan(session: Session):
    """A second booking, of its own reservation at a still-free table."""
    r = session.eval(
        "(goal (book Client:client-luis-soto Table:table-20 reservation-plnr-3 2026-09-25 19:00 2))"
    )
    assert r.outcome == "unico", r.text
    assert [w["verb"] for w in r.record["writes"]] == [
        "create",
        "change",
        "change",
        "change",
        "change",
        "assert",
        "assert",
        "change",
    ]
    assert r.record["plan"]["holds"] is True
    assert r.record["plan"]["writes"][0] == "(create Reservation reservation-plnr-3)"


def test_the_trace_says_which_rules_proved_it(session: Session):
    r = session.eval(
        "(goal (book Client:client-ana-perez Table:table-14 reservation-plnr-2 2026-09-21 20:00 8))"
    )
    assert any("by book" in line for line in r.trace)
    assert any("by table-fits" in line for line in r.trace)
    assert any("assigned_to" in line for line in r.trace)


def test_a_table_that_cannot_seat_them_is_never_written(session: Session):
    """The search refuses before the first write: table-3 seats four."""
    r = session.eval(
        "(goal (book Client:client-luis-soto Table:table-3 reservation-plnr-3 2026-09-22 20:00 9))"
    )
    assert r.outcome == "missing", r.text
    assert (
        session.world.store.doc(DocId.of("Reservation", "reservation-plnr-9")) is None
    )
    assert r.record["writes"] == []


def test_a_finished_reservation_can_be_confirmed_by_its_transition(session: Session):
    r = session.eval("(goal (confirm Reservation:reservation-2026-09-11-luis-soto))")
    assert r.outcome == "unico", r.text
    doc = session.world.store.doc(
        DocId.of("Reservation", "reservation-2026-09-11-luis-soto")
    )
    assert doc.payload["status"] == "confirmed"


def test_a_transition_is_a_rule_and_the_guard_is_its_condition(session: Session):
    """pending → seated has no edge, so no rule proves the transition."""
    r = session.eval(
        '(goal (transition Reservation:reservation-2026-09-11-luis-soto status "Reservation.status" pending seated))'
    )
    assert r.outcome == "missing", r.text


def test_the_guard_of_an_edge_is_read_from_its_relation_doc(session: Session):
    r = session.eval(
        "(goal (guard State:state-reservation-pending State:state-reservation-confirmed ?condition))"
    )
    assert r.text == '?condition = "party_size <= 8"', r.text
