"""Surface tokenizer + desugarer: positional grammar -> s-expression.

Implements atom-surface-grammar-is-positional-and-order-agnostic: noun-first
and verb-first orders desugar to the same Meaning; every token must resolve
against the anchor table.
"""

from __future__ import annotations

from knowledge.core.anchors import AnchorRegistry
from knowledge.core.results import SemanticError
from knowledge.core.sexpr import Keyword, SExpr, Symbol


def desugar(tokens: list[str], registry: AnchorRegistry) -> SExpr | SemanticError:
    """Deterministically translate surface tokens into one s-expression."""
    words, projection, where = _split_projection(tokens)
    if not words:
        return SemanticError(symbol="", message="comando vacío.")

    kinds: list[tuple[str, str]] = []  # (token, kind|selector)
    for w in words:
        anchor = registry.lookup(w)
        if isinstance(anchor, SemanticError):
            kinds.append((w, "selector"))
        else:
            kinds.append((w, anchor.kind))

    verb = next((t for t, k in kinds if k == "operation"), None)
    if verb is None:
        first_unknown = next((t for t, k in kinds if k == "selector"), words[0])
        looked_up = registry.lookup(first_unknown)
        if isinstance(looked_up, SemanticError):
            return looked_up
        return SemanticError(
            symbol=first_unknown,
            message=f"'{first_unknown}' no es una operación conocida.",
        )

    nouns = [(t, k) for t, k in kinds if k == "model"]
    selectors = [t for t, k in kinds if k == "selector"]
    relations = [t for t, k in kinds if k == "relation"]
    exprs = [t for t, k in kinds if k == "expr"]

    if not nouns and not exprs:
        return SemanticError(
            symbol=verb,
            message=f"'{verb}' necesita un sustantivo (modelo) sobre el cual operar.",
        )

    if exprs and selectors:
        # derived relation applied to a selector: (expr-sym "selector")
        ref: SExpr = [Symbol(exprs[0]), selectors[0]]
    elif nouns:
        noun = nouns[0][0]
        if selectors:
            ref = [Symbol("doc"), Symbol(noun), selectors[0]]
        else:
            ref = [Symbol("docs"), Symbol(noun)]
        if exprs:
            ref = [Symbol(exprs[0]), selectors[0] if selectors else ref]
    else:
        ref = [Symbol(exprs[0])]

    if relations:
        ref = [Symbol("rel"), Symbol(relations[0]), ref]

    expr: SExpr = [Symbol(verb), ref]
    if where:
        expr += [Keyword("where"), where]
    if projection:
        expr += [Keyword("project"), Symbol(projection)]
    return expr


def _split_projection(tokens: list[str]) -> tuple[list[str], str | None, str | None]:
    """Strip trailing --<projection> and --where "<expr>" flags."""
    words: list[str] = []
    projection = where = None
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t == "--where" and i + 1 < len(tokens):
            where = tokens[i + 1]
            i += 2
        elif t.startswith("--"):
            projection = t[2:]
            i += 1
        else:
            words.append(t)
            i += 1
    return words, projection, where
