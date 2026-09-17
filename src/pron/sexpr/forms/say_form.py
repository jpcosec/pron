"""`(say alias …)` (spec 05, 13): a sentence the world declared, by its symbol. An action
alias takes one noun, `(say alias NOUN)`; a relation alias two, `(say alias SUBJECT OBJECT)`;
a composed alias takes its slots filled by nouns, its document name and its literal fields,
`(say alias (slot "$referent:M" NOUN [(alternatives …)]) … [(as "doc-name")] (field value) …)`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.kernel.ids import address_of
from pron.kernel.parts.noun_phrase import NounPhrase
from pron.kernel.parts.part import Part
from pron.kernel.parts.word import Word
from pron.sexpr.forms.form_error import FormError
from pron.sexpr.forms.syntax import form_head, is_clause, unvalue

if TYPE_CHECKING:
    from pron.sexpr.forms.compiler import Compiler


class SayForm:
    head = "say"

    def __call__(self, compiler: Compiler, symbol: Any, *args: Any) -> Part:
        w = compiler.words.alias(str(symbol))
        if w.kind == "alias-action":
            return _action(compiler, symbol, w, args)
        if w.kind == "alias-relation":
            return _relation(compiler, symbol, w, args)
        if w.kind == "alias-compose":
            return _compose(compiler, w, args)
        raise FormError(f"(say {symbol} …): an alias of kind {w.kind} is not a move")


def _action(compiler: Compiler, symbol: Any, w: Word, args: tuple[Any, ...]) -> Part:
    if len(args) != 1:
        raise FormError(f"(say {symbol} NOUN): an action alias takes one noun")
    return Part(
        "action",
        subject=compiler.noun(args[0]),
        verb=w,
        field_name=w.field_name,
        value=w.payload.get("value"),
        payload={"verb": w.payload.get("verb"), "alias": True},
    )


def _relation(compiler: Compiler, symbol: Any, w: Word, args: tuple[Any, ...]) -> Part:
    if len(args) != 2:
        raise FormError(f"(say {symbol} SUBJECT OBJECT): a relation alias takes two nouns")
    return Part(
        "assert", subject=compiler.noun(args[0]), object=compiler.noun(args[1]), verb=w
    )


def _compose(compiler: Compiler, w: Word, args: tuple[Any, ...]) -> Part:
    slots: dict[str, NounPhrase] = {}
    literals: dict[str, Any] = {}
    for arg in args:
        _argument(compiler, arg, slots, literals)
    part = Part("compose", verb=w, payload=literals)
    part.payload["_slots"] = slots
    return part


def _argument(
    compiler: Compiler, arg: Any, slots: dict[str, NounPhrase], literals: dict[str, Any]
) -> None:
    """A filled slot, the document's name, or a literal field."""
    h = form_head(arg)
    if h == "slot":
        slots[str(arg[1])] = _slot(compiler, arg)
    elif h == "as":
        literals["_name"] = str(arg[1])
    else:
        literals[h] = unvalue(arg[1])


def _slot(compiler: Compiler, arg: Any) -> NounPhrase:
    """`(slot "$…" NOUN [(alternatives "Model:doc" …)])`: the noun that fills it."""
    np = compiler.noun(arg[2])
    for extra in arg[3:]:
        if is_clause(extra, "alternatives"):
            np.alternatives = [address_of(str(e)) for e in extra[1:]]
    return np
