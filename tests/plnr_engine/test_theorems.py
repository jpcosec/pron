"""Theorems as data: read from a world's text, indexed, and chosen explicitly."""

from __future__ import annotations

import pytest

from plnr import TheoremError, Theorems, read_one, read_theorem
from plnr.theorems import ANTECEDENT, CONSEQUENT


def test_a_theorem_reads_from_its_form():
    t = read_theorem(read_one("(theorem t1 consequent (free ?x) (goal (is ?x Table)))"))
    assert (t.name, t.kind, t.head) == ("t1", CONSEQUENT, "free")
    assert len(t.body) == 1


def test_a_theorem_writes_back_as_the_same_form():
    text = "(theorem t1 consequent (free ?x) (goal (is ?x Table)))"
    assert read_theorem(read_one(text)).as_form() == read_one(text)


def test_the_world_file_loads(theorems):
    assert len(theorems) >= 8
    assert "transition-legal" in theorems.names()


def test_consequents_are_indexed_by_head(theorems):
    names = [t.name for t in theorems.consequents("condition-holds")]
    assert names == ["condition-none", "condition-met"]


def test_antecedents_are_separate(theorems):
    assert [t.name for t in theorems.antecedents("edge")] == ["note-assignment"]
    assert [t.kind for t in theorems.antecedents("edge")] == [ANTECEDENT]


def test_use_picks_exactly_which_theorems_and_in_what_order(theorems):
    chosen = list(theorems.consequents("condition-holds", ["condition-met"]))
    assert [t.name for t in chosen] == ["condition-met"]


@pytest.mark.parametrize(
    "text",
    [
        "(theorem t1 sideways (free ?x) (succeed))",
        "(theorem t1 consequent free (succeed))",
        "(rule t1 consequent (free ?x) (succeed))",
    ],
)
def test_a_malformed_theorem_is_refused(text):
    with pytest.raises(TheoremError):
        Theorems().load(text)


def test_two_theorems_cannot_share_a_name():
    text = "(theorem t consequent (a) (succeed)) (theorem t consequent (b) (succeed))"
    with pytest.raises(TheoremError):
        Theorems().load(text)


def test_an_unknown_name_in_use_is_an_error(theorems):
    with pytest.raises(TheoremError):
        list(theorems.consequents("condition-holds", ["no-such-rule"]))
