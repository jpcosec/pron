"""Reading and writing forms: the text is the wire format, so it must round-trip."""

from __future__ import annotations

import pytest

from plnr import SexpError, Sym, read_all, read_one, write


def test_atoms_read_as_python_values():
    assert read_one("(a 1 2.5 true false nil)") == [
        Sym("a"),
        1,
        2.5,
        True,
        False,
        None,
    ]


def test_a_string_is_not_a_symbol():
    form = read_one('(where ?t "capacity >= 6")')
    assert form[2] == "capacity >= 6"
    assert not isinstance(form[2], Sym)


def test_symbols_compare_as_names():
    assert read_one("(goal x)")[1] == "x"


def test_write_reads_back(tmp_path):
    text = '(and (goal (where ?t "zone = \\"terrace\\"")) (find all ?t (succeed)))'
    assert read_one(write(read_one(text))) == read_one(text)


def test_comments_and_whitespace_are_skipped():
    assert read_all("; a comment\n(a)\n(b) ; trailing\n") == [[Sym("a")], [Sym("b")]]


def test_nested_quotes_survive():
    assert read_one('("say \\"hi\\"")')[0] == 'say "hi"'


@pytest.mark.parametrize("text", ["(", ")", "(a))", '("unterminated'])
def test_bad_text_is_an_error(text):
    with pytest.raises(SexpError):
        read_all(text)


def test_read_one_wants_exactly_one():
    with pytest.raises(SexpError):
        read_one("(a) (b)")


def test_booleans_are_not_numbers():
    assert write(True) == "true"
    assert write(1) == "1"
