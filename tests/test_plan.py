"""Running a plan: nothing is written, and what would be written comes back as forms.

The composed move ("book her a table") is the case that matters: in a fixed-construction
surface it needs a construction and an alias shape; here it is one theorem in the world's
own file, and the engine that runs it has never heard of a reservation.
"""

from __future__ import annotations

from plnr import MemoryWorld, WorldError, read_one, run


def test_a_plan_that_holds_reports_its_values(world, theorems):
    plan = run(read_one('(goal (where ?t "capacity >= 6"))'), world)
    assert plan
    assert plan.value("?t") == "t12"
    assert plan.writes == []


def test_a_plan_that_does_not_hold_says_why(world, theorems):
    plan = run(read_one('(goal (where ?t "capacity >= 99"))'), world)
    assert not plan
    assert plan.bindings is None
    assert "no solution" in plan.reason
    assert plan.trace


def test_a_malformed_goal_is_an_answer_not_a_crash(world, theorems):
    plan = run(read_one("(goal (delicious ?t))"), world, theorems)
    assert not plan
    assert "malformed goal" in plan.reason


def test_the_budget_refusal_is_also_an_answer(world, theorems):
    plan = run(read_one("(goal (is ?t Table))"), world, theorems, budget=1)
    assert not plan
    assert "gave up" in plan.reason
    assert plan.spent >= 1


def test_booking_writes_nothing_to_the_world(world, theorems):
    goal = read_one("(goal (book ana 6 terrace r-new ?table))")
    plan = run(goal, world, theorems)
    assert plan
    assert plan.value("?table") == "t12"
    assert world.model_of("r-new") is None
    assert world.payload("t12").get("busy") is None
    assert ("assigned_to", "r-new", "t12") not in set(world.edges())


def test_booking_hands_over_exactly_what_to_write(world, theorems):
    plan = run(read_one("(goal (book ana 6 terrace r-new ?t))"), world, theorems)
    assert plan.as_forms() == [
        "(create Reservation r-new)",
        "(change r-new party_size 6)",
        '(change r-new status "pending")',
        "(assert booked_by r-new ana)",
        "(assert assigned_to r-new t12)",
        "(change t12 busy true)",
    ]


def test_the_forward_theorem_is_the_last_write(world, theorems):
    """note-assignment is an antecedent theorem: it fires because assigned_to was asserted,
    and what it concludes is pending like everything else."""
    plan = run(read_one("(goal (book ana 6 terrace r-new ?t))"), world, theorems)
    assert plan.writes[-1] == ["change", "t12", "busy", True]


def test_a_later_goal_of_the_same_plan_sees_the_earlier_assertion(world, theorems):
    goal = read_one(
        """(and (goal (book ana 6 terrace r-new ?t))
                (goal (field r-new status ?status))
                (goal (edge assigned_to r-new ?same)))"""
    )
    plan = run(goal, world, theorems)
    assert plan
    assert plan.value("?status") == "pending"
    assert plan.value("?same") == plan.value("?t")


def test_a_plan_that_dies_after_asserting_leaves_no_writes(world, theorems):
    """The overlay of a refused plan is thrown away whole: a half-done move cannot escape."""
    goal = read_one("(and (goal (book ana 6 terrace r-new ?t)) (fail))")
    plan = run(goal, world, theorems)
    assert not plan
    assert plan.writes == []
    assert world.model_of("r-new") is None


def test_booking_backtracks_to_a_table_that_fits(world, theorems):
    world.link("assigned_to", "r-9", "t12")  # t12 taken: the plan must reach t14
    plan = run(read_one("(goal (book ana 6 terrace r-new ?t))"), world, theorems)
    assert plan
    assert plan.value("?t") == "t14"


def test_booking_refuses_when_nothing_fits(world, theorems):
    plan = run(read_one("(goal (book ana 40 terrace r-new ?t))"), world, theorems)
    assert not plan
    assert plan.writes == []


def test_the_trace_of_a_plan_shows_the_pending_writes(world, theorems):
    plan = run(read_one("(goal (book ana 6 terrace r-new ?t))"), world, theorems)
    text = "\n".join(plan.trace)
    assert "by book" in text
    assert "(pending)" in text
    assert "then note-assignment" in text


def test_a_plan_reports_the_variables_of_the_goal_and_no_others(world, theorems):
    """A theorem renames its variables on every use; those names are the search's, not the
    answer's."""
    goal = read_one("(goal (book ana 6 terrace r-new ?t))")
    plan = run(goal, world, theorems)
    assert set(plan.answers()) == {"?t"}
    assert plan.answers()["?t"] == "t12"
    # the raw bindings do carry the renamed ones; answers() is the door they do not pass
    assert any("#" in k for k in plan.bindings)  # type: ignore[union-attr]


def test_a_refused_plan_reports_no_answers(world, theorems):
    plan = run(read_one("(goal (free ?t))"), world, theorems, budget=1)
    assert plan.answers() == {}


class Rude(MemoryWorld):
    """A world that cannot answer, the way a store does when a name is not there."""

    def payload(self, _doc):
        raise WorldError("no such document named 'nothing'", absent=True)


class Refusing(MemoryWorld):
    """A world whose reads fail for a reason that is not a missing name."""

    def matches(self, _doc, _predicate):
        raise WorldError("no evaluator understands the predicate: 'gibberish'")


def test_a_name_the_world_does_not_have_is_a_refusal_not_a_crash():
    plan = run(read_one("(goal (field nothing title ?t))"), Rude())
    assert not plan
    assert plan.failure == "absent"
    assert "no such document" in plan.reason


def test_a_world_that_refuses_is_an_error_not_a_missing_noun():
    plan = run(read_one('(goal (where nothing "gibberish"))'), Refusing())
    assert not plan
    assert plan.failure == "world"
    assert "gibberish" in plan.reason
