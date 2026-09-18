"""A goal answered over the real stores (spec 13): the search reads sldb and kgdb, and the
rules it uses are documents of the world, not cases of the engine."""

from __future__ import annotations

from pron.session import Session


def test_a_goal_proved_by_a_theorem_finds_the_free_tables(session: Session):
    """table-3 is taken by the world's own reservation; the rest are free."""
    r = session.eval("(goal (find all ?t (goal (free ?t))))")
    assert r.outcome == "unico", r.text
    assert (
        r.text == "?t = (Table:table-5 Table:table-12 Table:table-14 Table:table-20)"
    ), r.text


def test_a_rule_reads_a_field_and_compares_it(session: Session):
    r = session.eval("(goal (find all ?t (goal (fits ?t 8))))")
    assert r.text == "?t = (Table:table-14)", r.text


def test_a_rule_chains_into_another_rule(session: Session):
    r = session.eval("(goal (find all ?t (goal (fits ?t 6))))")
    assert r.text == "?t = (Table:table-12 Table:table-14)", r.text


def test_the_plan_of_a_read_move_writes_nothing(session: Session):
    r = session.eval("(goal (free ?t))")
    assert r.record["writes"] == []
    assert r.record["plan"]["holds"] is True
    assert r.record["plan"]["writes"] == []


def test_the_queries_the_search_made_are_recorded(session: Session):
    r = session.eval("(goal (fits ?t 8))")
    assert any("Table" in q for q in r.record["queries"]), r.record["queries"]


def test_the_trace_says_which_theorem_proved_it(session: Session):
    r = session.eval("(goal (fits ?t 8))")
    assert any("by table-fits" in line for line in r.trace)


def test_a_goal_the_world_cannot_answer_is_missing(session: Session):
    r = session.eval("(goal (delicious ?t))")
    assert r.outcome == "error"
    assert "no primitive and no theorem" in r.text


def test_a_goal_that_holds_nowhere_is_missing(session: Session):
    r = session.eval("(goal (fits ?t 400))")
    assert r.outcome == "missing", r.text


def test_a_malformed_goal_is_an_error(session: Session):
    r = session.eval("(goal)")
    assert r.outcome == "error"
    assert "needs a goal" in r.text
