"""What a failed branch costs: nothing. Pending writes travel with the answer, not on the
engine.

These are the tests that caught the first version, which kept one overlay on the engine and
hoped backtracking would sort itself out: a branch that wrote and then died left its writes
where the next branch could see them. The fix is not a rollback — it is that every answer
carries its own overlay, so there is nothing to undo.

Note what is *not* a bug: two answers to `book` may seat the party at two different tables.
That is the world having two free tables, and each answer is a plan of its own.
"""

from __future__ import annotations

from plnr import Engine, MemoryWorld, Overlay, Sym, ground, read_one

BOOK = "(goal (book ana 6 terrace r-new ?t))"


def answers(world, theorems, goal=BOOK):
    """Every answer, each with the writes that answer would make."""
    engine = Engine(world, theorems)
    out = []
    for b, ov in engine.solve(read_one(goal), overlay=Overlay(world)):
        out.append((b, [list(w) for w in ov.all_writes()]))
    return out


def test_a_dead_branch_does_not_narrow_the_next_one(world, theorems):
    """The first alternative books t12 and then dies. The second asks for the free tables:
    if the dead branch's assertion were still around, only one would be free."""
    goal = """(or (and (goal (book ana 6 terrace r1 ?t)) (fail))
                  (find (at-least 2) ?free (goal (free ?free))))"""
    engine = Engine(world, theorems)
    _, ov = next(engine.solve(read_one(goal), overlay=Overlay(world)))
    b, _ = next(engine.solve(read_one(goal), overlay=Overlay(world)))
    assert ground(Sym("?free"), b) == ["t12", "t14"]
    assert ov.all_writes() == []


def test_each_answer_is_a_plan_of_its_own(world, theorems):
    for bindings, writes in answers(world, theorems):
        seated = bindings["?t"]
        assigned = [w[3] for w in writes if w[:2] == ["assert", "assigned_to"]]
        busy = [w[1] for w in writes if w[:2] == ["change", "busy"] or w[2] == "busy"]
        assert assigned == [seated]
        assert busy == [seated]


def test_the_second_answer_is_not_scored_over_the_first_ones_writes(world, theorems):
    """Two tables fit, so both answers must name a table the world had free."""
    found = [ground(Sym("?t"), b) for b, _ in answers(world, theorems)]
    assert found == ["t12", "t14"]


def test_a_failed_branch_is_an_overlay_nobody_reads_again(world, theorems):
    engine = Engine(world, theorems)
    goal = read_one("(or (and (goal (book ana 6 terrace r1 ?t)) (fail)) (succeed))")
    found = next(engine.solve(goal, overlay=Overlay(world)), None)
    assert found is not None
    assert found[1].all_writes() == []


def test_find_leaves_nothing_pending(world, theorems):
    engine = Engine(world, theorems)
    goal = read_one("(find all ?t (goal (book ana 6 terrace r1 ?t)))")
    found = next(engine.solve(goal, overlay=Overlay(world)), None)
    assert found is not None
    assert found[1].all_writes() == []


def test_not_leaves_nothing_pending(world, theorems):
    """Nobody seats 40, so the negation holds — over a goal that would have written."""
    engine = Engine(world, theorems)
    goal = read_one("(not (goal (book ana 40 terrace r1 ?t)))")
    found = next(engine.solve(goal, overlay=Overlay(world)), None)
    assert found is not None
    assert found[1].all_writes() == []


def test_a_later_step_of_the_same_branch_still_sees_the_earlier_write(world, theorems):
    """Forking must not hide the branch from itself."""
    engine = Engine(world, theorems)
    goal = read_one("(and (goal (book ana 6 terrace r-new ?t)) (goal (field t12 busy ?b)))")
    found = next(engine.solve(goal, overlay=Overlay(world)), None)
    assert found is not None
    assert ground(Sym("?b"), found[0]) is True


def test_an_outer_overlay_is_never_written_by_a_search(world, theorems):
    """A plan searched over somebody else's pending state inherits it and adds to a fork."""
    outer = Overlay(world)
    outer.set_field("r-1", "status", "confirmed")
    engine = Engine(world, theorems)
    found = next(engine.solve(read_one(BOOK), overlay=Overlay(outer)), None)
    assert found is not None
    assert [list(w) for w in outer.log] == [["change", "r-1", "status", "confirmed"]]
    assert found[1].all_writes()[0] == ["change", "r-1", "status", "confirmed"]


def test_the_world_is_still_the_world_after_a_search(world, theorems):
    before = {d: dict(world.payload(d)) for d in world.docs()}
    answers(world, theorems)
    after = {d: dict(world.payload(d)) for d in world.docs()}
    assert before == after


def test_a_memory_world_with_nothing_in_it_simply_finds_nothing():
    empty = MemoryWorld()
    engine = Engine(empty)
    assert next(engine.solve(read_one("(goal (is ?d Table))")), None) is None
