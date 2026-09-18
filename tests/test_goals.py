"""The goal language over a world: reading, control, backtracking and the budget."""

from __future__ import annotations

import pytest

from plnr import Budget, Engine, Exhausted, GoalError, Sym, ground, read_one, solutions


def answers(goal, world, theorems=None, var="?t"):
    return [ground(Sym(var), b) for b in solutions(read_one(goal), world, theorems)]


# -- primitives ----------------------------------------------------------------------


def test_is_enumerates_a_class(world):
    assert answers("(goal (is ?t Table))", world) == ["t10", "t12", "t14"]


def test_is_checks_a_named_document(world):
    assert answers("(goal (is t12 Table))", world, var="?t") == ["?t"]
    assert answers("(goal (is t12 Client))", world) == []


def test_is_reads_the_class_of_a_document(world):
    assert answers("(goal (is t12 ?m))", world, var="?m") == ["Table"]


def test_where_asks_the_store_for_the_predicate(world):
    assert answers('(goal (where ?t "capacity >= 6"))', world) == ["t12", "t14"]


def test_field_reads_a_value_and_can_run_backwards(world):
    assert answers("(goal (field t12 capacity ?c))", world, var="?c") == [6]
    assert answers("(goal (field ?t zone terrace))", world) == ["t12", "t14"]


def test_edge_matches_in_every_direction(world):
    assert answers("(goal (edge booked_by r-1 ?c))", world, var="?c") == ["ana"]
    assert answers("(goal (edge ?r r-1 ana))", world, var="?r") == ["booked_by"]


def test_compare_is_the_one_primitive_that_reads_nothing(world):
    assert answers("(goal (compare >= 8 6))", world, var="?x") == ["?x"]
    assert answers("(goal (compare >= 2 6))", world) == []


def test_compare_needs_ground_sides(world):
    with pytest.raises(GoalError):
        solutions(read_one("(goal (compare >= ?a 6))"), world)


# -- control -------------------------------------------------------------------------


def test_and_threads_bindings_and_intersects(world):
    goal = '(and (goal (where ?t "capacity >= 6")) (goal (field ?t zone terrace)))'
    assert answers(goal, world) == ["t12", "t14"]


def test_and_of_nothing_succeeds_once(world):
    assert len(solutions(read_one("(and)"), world)) == 1


def test_or_gives_every_alternative_on_backtracking(world):
    goal = "(or (goal (field ?t number 10)) (goal (field ?t number 14)))"
    assert answers(goal, world) == ["t10", "t14"]


def test_not_succeeds_once_and_binds_nothing(world):
    assert answers("(not (goal (is nobody Client)))", world, var="?x") == ["?x"]
    assert answers("(not (goal (is ana Client)))", world) == []


def test_bind_names_a_value(world):
    assert answers("(bind ?n 6)", world, var="?n") == [6]


def test_fail_and_succeed(world):
    assert solutions(read_one("(fail)"), world) == []
    assert len(solutions(read_one("(succeed)"), world)) == 1


# -- find ----------------------------------------------------------------------------


def test_find_all_collects_the_set(world):
    goal = '(find all ?t (goal (where ?t "capacity >= 6")))'
    assert answers(goal, world) == [["t12", "t14"]]


def test_find_one_is_the_determiner_the(world):
    assert answers("(find 1 ?t (goal (field ?t zone hall)))", world) == [["t10"]]


def test_find_one_fails_when_there_are_two(world):
    assert answers("(find 1 ?t (goal (field ?t zone terrace)))", world) == []


def test_find_at_least_accepts_more(world):
    goal = "(find (at-least 2) ?t (goal (field ?t zone terrace)))"
    assert answers(goal, world) == [["t12", "t14"]]


def test_find_at_least_refuses_fewer(world):
    goal = "(find (at-least 2) ?t (goal (field ?t zone hall)))"
    assert answers(goal, world) == []


def test_find_of_an_empty_set_is_an_empty_list(world):
    goal = "(find all ?t (goal (field ?t zone basement)))"
    assert answers(goal, world) == [[]]


def test_find_wants_a_variable(world):
    with pytest.raises(GoalError):
        solutions(read_one("(find all x (succeed))"), world)


# -- errors and budget ---------------------------------------------------------------


def test_an_unknown_head_is_an_error_not_a_no(world):
    with pytest.raises(GoalError):
        solutions(read_one("(goal (unheard-of ?x))"), world)


def test_a_goal_that_is_not_a_form_is_an_error(world):
    with pytest.raises(GoalError):
        solutions(read_one("(and x)"), world)


def test_the_budget_stops_a_runaway_search(world, theorems):
    engine = Engine(world, theorems, budget=Budget(2))
    with pytest.raises(Exhausted):
        list(engine.solve(read_one("(goal (is ?t Table))")))


def test_the_budget_counts_goals(world):
    engine = Engine(world, budget=Budget(100))
    list(engine.solve(read_one('(goal (where ?t "capacity >= 6"))')))
    assert 0 < engine.budget.spent <= 100
