"""The seven older string refs, turned into forms (spec 05, 13): `model:M`, `field:M.f`,
`value:M.f=v`, `predicate:M:<where>`, `relation:R`, `doc:M:name`, `action:<verb> [M.f=v]`,
and `compose` with its steps as dictionaries, whose slots become the nouns that fill them.
"""

from __future__ import annotations

from typing import Any, Callable

from pron.kernel.sexp.read_write import Sym


def legacy_form(ref: str, steps: list[dict[str, Any]]) -> Any:
    if ref == "compose":
        return [Sym("move"), *(_step(s) for s in steps if s.get("do") in tuple(STEPS))]
    head, _, rest = ref.partition(":")
    if head not in HEADS:
        raise ValueError(f"not a ref: {ref!r}")
    return HEADS[head](rest)


def _field(rest: str) -> Any:
    m, f = rest.split(".", 1)
    return [Sym("field"), Sym(m), Sym(f)]


def _value(rest: str) -> Any:
    mf, v = rest.split("=", 1)
    m, f = mf.split(".", 1)
    return [Sym("value"), Sym(m), Sym(f), v]


def _predicate(rest: str) -> Any:
    m, where = rest.split(":", 1)
    return [Sym("where"), Sym(m), where]


def _action(rest: str) -> Any:
    verb, _, assign = rest.partition(" ")
    if not assign:
        return [Sym("action"), Sym(verb)]
    mf, value = assign.split("=", 1)
    m, f = mf.split(".", 1)
    return [Sym(verb), [Sym("it"), "it", Sym(m)], Sym(f), value]


HEADS: dict[str, Callable[[str], Any]] = {
    "model": lambda rest: [Sym("model"), Sym(rest)],
    "field": _field,
    "value": _value,
    "predicate": _predicate,
    "relation": lambda rest: [Sym("relation"), Sym(rest)],
    "doc": lambda rest: [Sym("doc"), rest],
    "action": _action,
}


def _step(s: dict[str, Any]) -> Any:
    return STEPS[s["do"]](s)


def _noun_of_slot(slot: str) -> Any:
    if slot == "$created":
        return [Sym("created")]
    kind, _, model = slot[1:].partition(":")
    if kind == "referent":
        return [Sym("it"), "it"] + ([Sym(model)] if model else [])
    return [Sym("a"), Sym(model)]


STEPS: dict[str, Callable[[dict[str, Any]], Any]] = {
    "create": lambda s: [Sym("create"), Sym(s["model"])],
    "assert": lambda s: [
        Sym("assert"),
        Sym(s["relation"]),
        _noun_of_slot(s["source"]),
        _noun_of_slot(s["target"]),
    ],
    "change": lambda s: [
        Sym("change"),
        _noun_of_slot(s["target"]),
        Sym(s["field"]),
        s["value"],
    ],
}
