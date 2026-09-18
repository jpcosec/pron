"""A noun as a form becomes a noun phrase (spec 02, 13): `(doc "Model:name" …)` gives its
documents, `(it …)`, `(them …)` and `(me …)` are referents of the dialogue, and `(the M …)`,
`(a M …)`, `(all M …)`, `(find M …)` describe documents with clauses — `where`, `named`,
`plural`, `asked`, `of`, `of-name`, `set`, `not-a-value` — that the session resolves later.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from pron.kernel.ids import address_of, model_of
from pron.kernel.parts.item import Item
from pron.kernel.parts.noun_phrase import NounPhrase
from pron.sexpr.forms.form_error import FormError
from pron.sexpr.forms.syntax import NOUN_HEADS, REFERENT_HEADS, form_head, unvalue

if TYPE_CHECKING:
    from pron.sexpr.forms.form_words import FormWords

Clause = Callable[[NounPhrase, Any], None]
DETERMINERS = {"a": "any", "all": "all", "find": "all"}


class NounCompiler:
    """One noun form, one noun phrase; the models it names checked against the lexicon."""

    def __init__(self, words: FormWords):
        self.words = words
        self.clauses: dict[str, Clause] = {**CLAUSES, "of": self._of}

    def __call__(self, form: Any) -> NounPhrase:
        head = form_head(form)
        if head not in NOUN_HEADS:
            raise FormError(f"not a noun: ({head} …)")
        if head == "doc":
            return self._given(form)
        if head in REFERENT_HEADS:
            return _referent(form, head)
        return self._described(form, head)

    def negated(self, form: Any) -> NounPhrase:
        """The noun of a `forget`: `(doc "RelationDoc:…" …)` names edges to negate, whose
        relations the session must assert (spec 14 §4); any other noun as usual."""
        ids = [str(x) for x in form[1:]] if form_head(form) == "doc" else []
        if not ids or any(model_of(e) != "RelationDoc" for e in ids):
            return self(form)
        for eid in ids:
            self.words.need_negatable(eid)
        return _given_phrase(ids)

    def _given(self, form: Any) -> NounPhrase:
        ids = [str(x) for x in form[1:]]
        for eid in ids:
            self.words.need_model(model_of(eid))
        return _given_phrase(ids)

    def _described(self, form: Any, head: str) -> NounPhrase:
        model = str(form[1])
        self.words.need_model(model)
        det = DETERMINERS.get(head, "the")
        np = NounPhrase(model, det, "plural" if det == "all" else "singular")
        for clause in form[2:]:
            ch = form_head(clause)
            if ch not in self.clauses:
                raise FormError(f"unknown clause in ({head} {model} …): ({ch} …)")
            self.clauses[ch](np, clause)
        return np

    def _of(self, np: NounPhrase, clause: Any) -> None:
        np.complements.append(self(clause[1]))


def _given_phrase(ids: list[str]) -> NounPhrase:
    np = NounPhrase(
        model_of(ids[0]) if ids else None,
        "the",
        "singular" if len(ids) == 1 else "plural",
    )
    np.given = [address_of(e) for e in ids]
    return np


def _referent(form: Any, head: str) -> NounPhrase:
    word = str(form[1]) if len(form) > 1 else head
    who = REFERENT_HEADS[head]
    number = "plural" if who == "plural" else "singular"
    item = Item("referent", word, number=number, meta={"who": who})
    np = NounPhrase(None, None, number, referent=item, items=[item])
    if len(form) > 2:
        np.hint = str(form[2])
    return np


def _where(np: NounPhrase, clause: Any) -> None:
    np.predicates.append(str(clause[1]))


def _named(np: NounPhrase, clause: Any) -> None:
    np.proper.append(str(clause[1]))


def _plural(np: NounPhrase, clause: Any) -> None:
    np.number = "plural"


def _asked(np: NounPhrase, clause: Any) -> None:
    np.interrogated = True


def _of_name(np: NounPhrase, clause: Any) -> None:
    np.complements.append([str(x) for x in clause[1:]])


def _set(np: NounPhrase, clause: Any) -> None:
    np.captures[str(clause[1])] = unvalue(clause[2])


def _not_a_value(np: NounPhrase, clause: Any) -> None:
    np.unknown_values.append((str(clause[1]), str(clause[2]), str(clause[3])))


CLAUSES: dict[str, Clause] = {
    "where": _where,
    "named": _named,
    "plural": _plural,
    "asked": _asked,
    "of-name": _of_name,
    "set": _set,
    "not-a-value": _not_a_value,
}
