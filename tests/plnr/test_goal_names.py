"""Nombres y negativas (spec 02, 13): lo que un mundo real tiene —documentos con nombre corto
y sin el prefijo del modelo— y lo que contesta cuando no lo tiene.

Lo que un nombre ausente produce es `missing`, como un sustantivo que no resolvió a nada;
lo que un store que se niega produce —un predicado que no entiende— es `error`. Ni uno ni
otro escriben.
"""

from __future__ import annotations

from pron.session import Session


def test_a_document_can_be_named_by_its_own_name(session: Session):
    """Un mundo de KB nombra sus documentos 'atom-cobranza-pago', no 'DomainAtom:…'."""
    r = session.eval("(goal (field table-3 capacity ?c))")
    assert r.outcome == "unico", r.text
    assert r.text == "?c = 4", r.text


def test_a_name_the_world_does_not_have_is_missing(session: Session):
    r = session.eval("(goal (field table-404 capacity ?c))")
    assert r.outcome == "missing", r.text
    assert r.record["writes"] == []


def test_an_export_id_that_does_not_exist_is_missing_too(session: Session):
    r = session.eval("(goal (field Table:table-404 capacity ?c))")
    assert r.outcome == "missing", r.text
    assert "no Table named" in r.text


def test_a_predicate_the_store_refuses_is_an_error(session: Session):
    r = session.eval('(goal (find all ?t (goal (where ?t "esto no es un predicado"))))')
    assert r.outcome == "error", r.text
    assert "no evaluator understands the predicate" in r.text
    assert r.record["writes"] == []


def test_a_goal_that_names_no_rule_is_an_error(session: Session):
    r = session.eval("(goal (invented-rule ?x))")
    assert r.outcome == "error", r.text
    assert "nothing proves" in r.text


def test_the_failure_of_a_plan_is_recorded_as_it_is(session: Session):
    r = session.eval("(goal (field table-404 capacity ?c))")
    assert r.record["plan"]["failure"] == "absent"
    r = session.eval("(goal (invented-rule ?x))")
    assert r.record["plan"]["failure"] == "malformed"
