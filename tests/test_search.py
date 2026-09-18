"""Search through theorems: chaining, backtracking, negation, and THUSE.

These are the tests that say what the layer is for — a rule written in a world's own file
decides the answer, and no name from that file appears in src/plnr.
"""

from __future__ import annotations

import pytest

from plnr import Engine, GoalError, Sym, ground, read_one, solutions


def answers(goal, world, theorems, var):
    return [ground(Sym(var), b) for b in solutions(read_one(goal), world, theorems)]


def test_a_theorem_proves_a_goal_the_world_never_stores(world, theorems):
    # "free" is nowhere in the documents: it is three goals in restaurant.theorems
    assert answers("(goal (free ?t))", world, theorems, "?t") == ["t12", "t14"]


def test_a_theorem_chains_into_another(world, theorems):
    assert answers("(goal (fits ?t 8))", world, theorems, "?t") == ["t14"]


def test_two_theorems_for_the_same_head_are_both_tried(world, theorems):
    # pending → confirmed has no guard (condition-none); confirmed → seated has one
    assert answers(
        "(goal (transition r-1 status pending confirmed))", world, theorems, "?x"
    ) == ["?x"]


def test_a_guarded_transition_holds_when_its_predicate_does(world, theorems):
    world.add("r-1", "Reservation", {"party_size": 4, "status": "confirmed"})
    assert answers(
        "(goal (transition r-1 status confirmed seated))", world, theorems, "?x"
    ) == ["?x"]


def test_the_same_transition_is_refused_when_the_guard_fails(world, theorems):
    world.add("r-1", "Reservation", {"party_size": 9, "status": "confirmed"})
    assert (
        answers("(goal (transition r-1 status confirmed seated))", world, theorems, "?x") == []
    )


def test_a_transition_with_no_edge_is_refused(world, theorems):
    assert answers("(goal (transition r-1 status pending seated))", world, theorems, "?x") == []


def test_backtracking_finds_the_second_answer_after_the_first_dies(world, theorems):
    # t12 fits 6 but not 8; the search must move on to t14 rather than give up
    goal = "(and (goal (free ?t)) (goal (fits ?t 8)))"
    assert answers(goal, world, theorems, "?t") == ["t14"]


def test_negation_inside_a_theorem_sees_the_world(world, theorems):
    world.link("assigned_to", "r-9", "t12")
    assert answers("(goal (free ?t))", world, theorems, "?t") == ["t14"]


def test_use_restricts_which_theorem_may_prove_a_goal(world, theorems):
    world.add("r-1", "Reservation", {"party_size": 4, "status": "confirmed"})
    with_guard = "(goal (condition-holds s-confirmed s-seated r-1) (use condition-met))"
    only_none = "(goal (condition-holds s-confirmed s-seated r-1) (use condition-none))"
    assert answers(with_guard, world, theorems, "?x") == ["?x"]
    assert answers(only_none, world, theorems, "?x") == []


def test_variables_of_two_uses_of_one_theorem_do_not_collide(world, theorems):
    goal = "(and (goal (fits ?a 2)) (goal (fits ?b 8)))"
    pairs = [
        (ground(Sym("?a"), b), ground(Sym("?b"), b))
        for b in solutions(read_one(goal), world, theorems)
    ]
    assert ("t10", "t14") in pairs
    assert all(b == "t14" for _, b in pairs)


def test_a_goal_nobody_can_prove_is_an_error_not_silence(world, theorems):
    with pytest.raises(GoalError):
        solutions(read_one("(goal (delicious ?t))"), world, theorems)


def test_the_trace_is_the_explanation_of_the_answer(world, theorems):
    engine = Engine(world, theorems)
    next(engine.solve(read_one("(goal (fits ?t 8))")))
    text = "\n".join(engine.trace)
    assert "goal (fits ?t 8)" in text
    assert "by table-fits" in text
    assert "goal (compare >= 8 8)" in text
