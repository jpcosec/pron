"""Bindings and unification: the reason a failed branch costs nothing."""

from __future__ import annotations

from plnr import EMPTY, Sym, ground, is_var, read_one, unify, variables
from plnr.terms import Bindings, refresh


def test_a_variable_is_a_question_mark_symbol():
    assert is_var(Sym("?t"))
    assert not is_var(Sym("t"))
    assert not is_var("?t not a symbol")


def test_binding_a_variable_leaves_the_old_binding_alone():
    before = EMPTY
    after = before.with_("?t", Sym("t12"))
    assert dict(before) == {}
    assert after["?t"] == "t12"


def test_unify_binds_and_then_checks():
    b = unify(read_one("(edge ?r ?s ?t)"), read_one("(edge booked_by r-1 ana)"), EMPTY)
    assert b is not None
    assert ground(Sym("?s"), b) == "r-1"
    assert unify(Sym("?s"), Sym("ana"), b) is None


def test_unify_is_two_way():
    b = unify(read_one("(f ?x b)"), read_one("(f a ?y)"), EMPTY)
    assert b is not None
    assert ground(Sym("?x"), b) == "a"
    assert ground(Sym("?y"), b) == "b"


def test_unify_walks_chains():
    b = Bindings({"?a": Sym("?b"), "?b": 6})
    assert ground(Sym("?a"), b) == 6
    assert unify(Sym("?a"), 6, b) is not None
    assert unify(Sym("?a"), 7, b) is None


def test_lists_must_have_the_same_length():
    assert unify(read_one("(a ?x)"), read_one("(a b c)"), EMPTY) is None


def test_true_is_not_one():
    assert unify(True, 1, EMPTY) is None


def test_ground_leaves_free_variables_as_they_are():
    b = EMPTY.with_("?a", 6)
    assert ground(read_one("(pair ?a ?b)"), b) == [Sym("pair"), 6, Sym("?b")]


def test_variables_are_listed_once_in_order():
    assert variables(read_one("(g ?b ?a ?b)")) == ["?b", "?a"]


def test_refresh_renames_per_use():
    once = refresh(read_one("(free ?t)"), 1)
    twice = refresh(read_one("(free ?t)"), 2)
    assert once != twice
    assert unify(once, twice, EMPTY) is not None  # they can still meet through a binding
