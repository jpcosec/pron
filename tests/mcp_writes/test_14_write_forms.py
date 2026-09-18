"""The write tools' JSON compiled to forms (spec 13, 14 §4): every value escaped by the
printer, the forms read back as what was sent, and arguments that make no form refused."""

from __future__ import annotations

import pytest

from pron.kernel.sexp.read_write import Sym, read_one
from pron.mcp.writes import ArgError, ContentForms, RuleForms


def test_a_create_escapes_every_kind_of_value():
    fields = {"name": 'Eva "E" \\ x', "n": 3, "f": 2.5, "ok": True, "no": None}
    form = ContentForms.doc_create("Client", {**fields, "tags": ["a", "b c"]}, "c-e")
    expr = read_one(form)
    assert expr[:3] == [Sym("create"), Sym("Client"), [Sym("as"), "c-e"]]
    assert dict((str(k), v) for k, v in expr[3:8]) == fields
    assert expr[8] == [Sym("tags"), [Sym("list"), "a", "b c"]]


def test_an_edit_is_one_move_of_its_ops():
    ops = [
        {"op": "set", "field": "notes", "value": "hi"},
        {"op": "add", "field": "tags", "value": "x"},
        {"op": "remove", "field": "tags"},
        {"op": "clean", "field": "notes"},
    ]
    form = ContentForms.doc_edit("Client:c", ops)
    assert form == (
        '(move (change (doc "Client:c") notes "hi") (add (doc "Client:c") tags "x") '
        '(remove (doc "Client:c") tags) (clean (doc "Client:c") notes))'
    )


@pytest.mark.parametrize(
    "call",
    [
        lambda: ContentForms.doc_create("Client) (forget", {}),
        lambda: ContentForms.doc_create("Client", {"a b": 1}),
        lambda: ContentForms.doc_create("Client", {"x": {"nested": 1}}),
        lambda: ContentForms.doc_edit("Client:c", []),
        lambda: ContentForms.doc_edit("Client:c", [{"op": "set", "field": "x"}]),
        lambda: ContentForms.doc_edit(
            "Client:c", [{"op": "clean", "field": "x", "value": 1}]
        ),
        lambda: ContentForms.doc_edit("Client:c", [{"op": "drop", "field": "x"}]),
        lambda: ContentForms.doc_forget("no-model"),
        lambda: RuleForms.rule_edit("r", {"name": "other"}),
    ],
)
def test_arguments_that_make_no_form_are_refused(call):
    with pytest.raises(ArgError):
        call()


def test_edges_and_rules_as_forms():
    assert (
        ContentForms.edge_assert("A:x", "rel", "B:y")
        == '(assert rel (doc "A:x") (doc "B:y"))'
    )
    assert (
        ContentForms.edge_expire("RelationDoc:r--A:x--B:y")
        == '(forget (doc "RelationDoc:r--A:x--B:y"))'
    )
    assert ContentForms.undo() == "(undo)"
    assert RuleForms.rule_edit("likes", {"cardinality": "one_to_one"}) == (
        '(move (change (doc "RelationTypeDoc:rt-likes") cardinality "one_to_one"))'
    )
    form = RuleForms.rule_declare("likes", {"source_types": ["Client"]})
    assert form == (
        '(create RelationTypeDoc (as "rt-likes") (title "likes") (name "likes") '
        '(source_types (list "Client")))'
    )
