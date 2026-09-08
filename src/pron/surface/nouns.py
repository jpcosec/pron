"""Noun phrases: from a run of classified items to a scope and predicates (spec 02).

A noun phrase is a head (a model word, an alias for a model, or a referent) with a
determiner before it and modifiers after it. Modifiers are, in order of trial:
a proper name ("the client Ana", "the bridges one"), a value word ("the pending
reservations"), a predicate alias with its slots ("on the terrace", "for 6"), or a
field word followed by a value ("with capacity 6"). Every modifier becomes one
sldb predicate. A modifier whose word belongs to a model outside the head's family
is skipped for this phrase and left for the sentence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pron.lexicon import Lexicon, Word
from pron.surface.tokens import Item

PREDICATE_STOP = {"and", "to", "as", "with"}
PRONOUNS = {"it": "singular", "her": "singular", "him": "singular", "them": "plural", "those": "plural"}


@dataclass
class NounPhrase:
    model: str | None                       # head model; None for a bare referent
    determiner: str | None                  # the | a | any | all | none
    number: str                             # singular | plural
    predicates: list[str] = field(default_factory=list)
    proper: list[str] = field(default_factory=list)   # proper names to resolve by key/name/doc
    referent: Item | None = None
    interrogated: bool = False
    items: list[Item] = field(default_factory=list)
    captures: dict[str, Any] = field(default_factory=dict)  # field literals seen inside the phrase (for compose $literals)
    unknown_values: list[tuple[str, str, str]] = field(default_factory=list)  # (model, field, text) missing enum values

    @property
    def scope(self) -> str:
        return f"st.{{{self.model}+}}" if self.model else ""

    def describe(self) -> str:
        head = self.model or (self.referent.text if self.referent else "?")
        return f"{self.determiner or ''} {head} [{'; '.join(self.predicates)}]{' ' + ','.join(self.proper) if self.proper else ''}".strip()


def find_noun_phrases(items: list[Item], lex: Lexicon) -> list[NounPhrase]:
    """Every noun phrase in the item list, left to right, non-overlapping."""
    phrases: list[NounPhrase] = []
    i = 0
    while i < len(items):
        np, used = _phrase_at(items, i, lex)
        if np is None:
            i += 1
            continue
        phrases.append(np)
        i += used
    return phrases


def _phrase_at(items: list[Item], i: int, lex: Lexicon) -> tuple[NounPhrase | None, int]:
    it = items[i]
    det = None
    start = i
    if it.kind == "det":
        det = _det_kind(it.text)
        i += 1
        if i >= len(items):
            return None, 0
        it = items[i]
    if it.kind == "referent" and it.meta.get("who") in ("singular", "plural"):
        np = NounPhrase(None, det, it.number or "singular", referent=it, items=[it])
        return np, i - start + 1
    if it.kind == "word" and it.words and it.words[0].kind in ("alias-action", "alias-compose", "alias-relation"):
        # "confirm it", "book her": the alias form swallowed the pronoun; it is still a referent
        last = it.text.split()[-1].lower()
        number = PRONOUNS.get(last)
        if number and det is None:
            fake = Item("referent", last, number=number, meta={"who": number, "implicit": True})
            return NounPhrase(None, None, number, referent=fake, items=[it]), 1
    # adjectives before the head: value words and predicate aliases ("the large tables", "the pending reservations")
    pre: list[Item] = []
    while it.kind == "word" and _head_model(it) is None and any(w.kind in ("value", "alias-predicate") for w in it.words):
        pre.append(it)
        i += 1
        if i >= len(items):
            return None, 0
        it = items[i]
    head = _head_model(it)
    if head is None:
        return None, 0
    number = it.number or ("plural" if det in ("all",) else "singular")
    if det is None and number == "plural":
        det = "all"
    interrogated = start > 0 and items[start - 1].kind == "wh"
    np = NounPhrase(head, det or ("the" if number == "singular" and not interrogated else "all"), number, interrogated=interrogated, items=[it])
    for adj in pre:
        if not _word_modifier(adj, None, np, lex):
            return None, 0
    j = i + 1
    while j < len(items):
        used = _modifier(items, j, np, lex)
        if not used:
            break
        j += used
    return np, j - start


def _det_kind(text: str) -> str:
    t = text.lower()
    if t in ("a", "an", "one", "any"):
        return "any"
    if t in ("all", "every", "all the", "these", "those"):
        return "all"
    return "the"


def _head_model(it: Item) -> str | None:
    if it.kind != "word":
        return None
    for w in it.words:
        if w.kind in ("model", "alias-model"):
            return w.model
    return None


def _modifier(items: list[Item], j: int, np: NounPhrase, lex: Lexicon) -> int:
    it = items[j]
    family = set(lex.world.family_of(np.model))
    if it.kind == "unknown" or (it.kind == "literal" and not it.meta.get("marker")):
        # a proper name in name position: "the client Ana", "the bridges one"
        if it.kind == "unknown" and it.text.lower() in PREDICATE_STOP:
            return 0
        np.proper.append(it.text); np.items.append(it)
        return 1
    if it.kind == "number":
        np.proper.append(str(it.meta["value"])); np.items.append(it)
        return 1
    if it.kind == "of" and j + 1 < len(items) and items[j + 1].kind in ("unknown", "literal"):
        np.proper.append(items[j + 1].text); np.items += [it, items[j + 1]]
        return 2
    if it.kind != "word":
        return 0
    nxt = items[j + 1] if j + 1 < len(items) else None
    return _word_modifier(it, nxt, np, lex)


def _word_modifier(it: Item, nxt: Item | None, np: NounPhrase, lex: Lexicon) -> int:
    """One word item as a modifier of np: a value, a predicate alias, or a field with a value. Returns items used."""
    family = set(lex.world.family_of(np.model))
    for w in it.words:
        if w.kind == "value" and w.model in family:
            np.predicates.append(f'{w.field_name} = "{w.payload["value"]}"'); np.items.append(it)
            return 1
        if w.kind == "alias-predicate" and w.model in family:
            where, unknown = _fill_predicate(w, it, lex)
            if unknown:
                np.unknown_values.append(unknown)
            np.predicates.append(where); np.items.append(it)
            return 1
        if w.kind in ("field", "alias-field") and w.model in family:
            if it.slots:
                value = _slot_value(it)
                np.predicates.append(f"{w.field_name} = {_literal(value)}"); np.captures[w.field_name] = value; np.items.append(it)
                return 1
            if nxt is not None and nxt.kind in ("number", "literal", "unknown"):
                value = nxt.meta.get("value", nxt.text)
                np.predicates.append(f"{w.field_name} = {_literal(value)}"); np.captures[w.field_name] = value; np.items += [it, nxt]
                return 2
    return 0


def _fill_predicate(w: Word, it: Item, lex: Lexicon) -> tuple[str, tuple[str, str, str] | None]:
    """predicate:M:<where> with N / Z / X slots substituted; a Z that is not a known value is reported."""
    where = w.ref.split(":", 2)[2]
    unknown = None
    for slot, value in it.slots.items():
        if slot == "Z":
            fld = where.split("=")[0].strip().split()[0]
            known = {v.payload["value"] for v in lex.values_of(w.model, fld)}
            if known and value not in known:
                unknown = (w.model, fld, value)
            where = where.replace("Z", f'"{value}"')
        else:
            where = where.replace(slot, str(value))
    return where, unknown


def _slot_value(it: Item) -> Any:
    for key in ("N", "DAY", "TIME", "Z", "X"):
        if key in it.slots:
            return it.slots[key]
    return it.text


def _literal(value: Any) -> str:
    return str(value) if isinstance(value, (int, float)) else f'"{value}"'
