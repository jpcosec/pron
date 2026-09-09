"""Noun phrases: from a run of classified items to a scope and predicates (spec 02).

A noun phrase is a head (a model word, an alias for a model, or a referent) with a
determiner before it and modifiers after it. Modifiers are, in order of trial:
a proper name ("the client Ana", "the bridges one"), a value word ("the pending
reservations"), a predicate alias with its slots ("on the terrace", "for 6"), or a
field word followed by a value ("with capacity 6"). Every modifier becomes one
sldb predicate. A modifier whose word belongs to a model outside the head's family
is skipped for this phrase and left for the sentence.

"of X" after the head, and "X's" before it, are complements: what X is gets decided
at resolution (spec 02), in this order: a value of a field of the head, a document of
another class the head is related to (then the phrase crosses the edges of that
relation with its own predicates), a proper name of the head itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pron.lexicon import Lexicon, Word
from pron.surface.tokens import Item

PREDICATE_STOP = {"and", "to", "as", "with"}
PRONOUNS = {
    "it": "singular",
    "her": "singular",
    "him": "singular",
    "them": "plural",
    "those": "plural",
}


@dataclass
class NounPhrase:
    model: str | None  # head model; None for a bare referent
    determiner: str | None  # the | a | any | all | none
    number: str  # singular | plural
    predicates: list[str] = field(default_factory=list)
    proper: list[str] = field(
        default_factory=list
    )  # proper names to resolve by key/name/doc
    referent: Item | None = None
    interrogated: bool = False
    items: list[Item] = field(default_factory=list)
    captures: dict[str, Any] = field(
        default_factory=dict
    )  # field literals seen inside the phrase (for compose $literals)
    unknown_values: list[tuple[str, str, str]] = field(
        default_factory=list
    )  # (model, field, text) missing enum values
    complements: list[Any] = field(
        default_factory=list
    )  # after "of" / genitive: a run of proper-name tokens (list[str]) or a nested NounPhrase

    @property
    def scope(self) -> str:
        return f"st.{{{self.model}+}}" if self.model else ""

    def describe(self) -> str:
        head = self.model or (self.referent.text if self.referent else "?")
        comps = " ".join(
            "of " + (c.describe() if isinstance(c, NounPhrase) else " ".join(c))
            for c in self.complements
        )
        return f"{self.determiner or ''} {head} [{'; '.join(self.predicates)}]{' ' + ','.join(self.proper) if self.proper else ''}{' ' + comps if comps else ''}".strip()


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


def _phrase_at(
    items: list[Item], i: int, lex: Lexicon
) -> tuple[NounPhrase | None, int]:
    it = items[i]
    det = None
    start = i
    if it.kind == "det":
        det = _det_kind(it.text)
        i += 1
        if i >= len(items):
            return None, 0
        it = items[i]
    genitive: list[str] = []
    if it.kind == "unknown":
        k = i
        while (
            k < len(items)
            and items[k].kind in ("unknown", "number")
            and not items[k].text.endswith("'s")
        ):
            k += 1
        if (
            k < len(items)
            and items[k].kind == "unknown"
            and items[k].text.endswith("'s")
            and k + 1 < len(items)
            and _head_model(items[k + 1]) is not None
        ):
            genitive = [x.text for x in items[i:k]] + [items[k].text[:-2]]
            i = k + 1
            it = items[i]
    if it.kind == "referent" and it.meta.get("who") in ("singular", "plural"):
        np = NounPhrase(None, det, it.number or "singular", referent=it, items=[it])
        return np, i - start + 1
    if (
        it.kind == "word"
        and it.words
        and it.words[0].kind in ("alias-action", "alias-compose", "alias-relation")
    ):
        # "confirm it", "book her": the alias form swallowed the pronoun; it is still a referent
        last = it.text.split()[-1].lower()
        number = PRONOUNS.get(last)
        if number and det is None:
            fake = Item(
                "referent", last, number=number, meta={"who": number, "implicit": True}
            )
            return NounPhrase(None, None, number, referent=fake, items=[it]), 1
    # adjectives before the head: value words and predicate aliases ("the large tables", "the pending reservations")
    pre: list[Item] = []
    while (
        it.kind == "word"
        and _head_model(it) is None
        and any(w.kind in ("value", "alias-predicate") for w in it.words)
    ):
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
    interrogated = (
        start > 0
        and items[start - 1].kind == "wh"
        and items[start - 1].meta.get("question") in ("what", "who", "how_many")
    )
    np = NounPhrase(
        head,
        det or ("the" if number == "singular" and not interrogated else "all"),
        number,
        interrogated=interrogated,
        items=[it],
    )
    if genitive:
        np.complements.append(genitive)
        np.items = items[start:i] + [it]
    for adj in pre:
        if not _word_modifier(adj, [], np, lex):
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
    if it.kind == "literal" and it.meta.get("kind") in ("date", "time"):
        return _dated(it, np, lex)
    if (
        it.kind == "unknown"
        and it.text.lower() in ("for", "on", "at")
        and j + 1 < len(items)
        and items[j + 1].kind == "literal"
        and items[j + 1].meta.get("kind") in ("date", "time")
    ):
        used = _dated(items[j + 1], np, lex)
        if used:
            np.items.append(it)  # the preposition belongs to the phrase too
        return 1 + used if used else 0
    if it.kind == "unknown" or (
        it.kind == "literal" and not it.meta.get("marker") and not it.meta.get("kind")
    ):
        # a proper name in name position: "the client Ana", "the bridges one"
        if it.kind == "unknown" and it.text.lower() in PREDICATE_STOP:
            return 0
        np.proper.append(it.text)
        np.items.append(it)
        return 1
    if it.kind == "number":
        np.proper.append(str(it.meta["value"]))
        np.items.append(it)
        return 1
    if it.kind == "of" and j + 1 < len(items):
        nxt = items[j + 1]
        if (
            nxt.kind == "word"
            and _head_model(nxt) is None
            and _word_modifier(nxt, items[j + 2 :], np, lex)
        ):
            np.items.append(it)  # "of pron": a value of a field of the head
            return 2
        if nxt.kind == "det" or _head_model(nxt) is not None:
            inner, used = _phrase_at(
                items, j + 1, lex
            )  # "of the reservations of Luis": a nested phrase
            if inner is not None:
                np.complements.append(inner)
                np.items += [it, *inner.items]
                return 1 + used
        run = _proper_run(items, j + 1)
        if run:
            np.complements.append([x.text for x in run])
            np.items += [it, *run]
            return 1 + len(run)
        return 0
    if it.kind != "word":
        return 0
    return _word_modifier(it, items[j + 1 :], np, lex)


def _proper_run(items: list[Item], j: int) -> list[Item]:
    """The unknown, number and plain-literal items after "of", up to the next known word, determiner,
    stop word or dated literal."""
    run: list[Item] = []
    while j < len(items):
        it = items[j]
        if it.kind in ("unknown", "number") or (
            it.kind == "literal"
            and not it.meta.get("marker")
            and not it.meta.get("kind")
        ):
            if it.kind == "unknown" and it.text.lower() in PREDICATE_STOP | {
                "for",
                "on",
                "at",
            }:
                break
            run.append(it)
            j += 1
        else:
            break
    return run


def _dated(it: Item, np: NounPhrase, lex: Lexicon) -> int:
    """A date or time literal as a modifier: the head's field of that kind, or named so."""
    assert np.model is not None
    kind = it.meta.get("kind")
    for f in lex.world.schema(np.model, lex.stores):
        if f["name"] == kind or f["kind"] == kind:
            np.predicates.append(f'{f["name"]} = "{it.meta["value"]}"')
            np.items.append(it)
            return 1
    return 0


def _word_modifier(
    it: Item, following: list[Item] | None, np: NounPhrase, lex: Lexicon
) -> int:
    """One word item as a modifier of np: a value, a predicate alias, or a field with a value. Returns items used."""
    assert np.model is not None
    following = following or []
    family = set(lex.world.family_of(np.model))
    nxt = following[0] if following else None
    for w in it.words:
        if w.kind == "value" and w.model in family:
            np.predicates.append(f'{w.field_name} = "{w.payload["value"]}"')
            np.items.append(it)
            return 1
        if w.kind == "alias-predicate" and w.model in family:
            where, unknown = _fill_predicate(w, it, lex)
            if unknown:
                np.unknown_values.append(unknown)
            np.predicates.append(where)
            np.items.append(it)
            return 1
        if w.kind in ("field", "alias-field") and w.model in family:
            assert w.field_name is not None
            if it.slots:
                value = _slot_value(it)
                np.predicates.append(f"{w.field_name} = {_literal(value)}")
                np.captures[w.field_name] = value
                np.items.append(it)
                return 1
            if nxt is not None and nxt.kind in ("number", "literal", "unknown"):
                value, used = value_run(
                    following, string_field=field_is_string(lex, w.model, w.field_name)
                )
                np.predicates.append(f"{w.field_name} = {_literal(value)}")
                np.captures[w.field_name] = value
                np.items += [it, *following[:used]]
                return 1 + used
    return 0


def field_is_string(lex: Lexicon, model: str | None, field_name: str | None) -> bool:
    if not model or not field_name:
        return False
    for f in lex.world.schema(model, lex.stores):
        if f["name"] == field_name:
            return f["kind"] == "string"
    return False


def value_run(following: list[Item], string_field: bool) -> tuple[Any, int]:
    """The value after a field word: one literal or number, or for a string field the whole run of
    unknown and number items ("Ana Rojas", "9 5555 1234") up to the next known item."""
    first = following[0]
    if first.kind == "literal":
        return first.meta.get("value", first.text), 1
    if not string_field:
        return first.meta.get("value", first.text), 1
    parts, used = [], 0
    for it in following:
        if it.kind in ("unknown", "number") and it.text.lower() not in PREDICATE_STOP:
            parts.append(it.text)
            used += 1
        else:
            break
    return " ".join(parts), used


def _fill_predicate(
    w: Word, it: Item, lex: Lexicon
) -> tuple[str, tuple[str, str, str] | None]:
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
