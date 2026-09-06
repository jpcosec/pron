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
    words, projection = _split_projection(tokens)
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
        return registry.lookup(first_unknown) if isinstance(registry.lookup(first_unknown), SemanticError) else SemanticError(symbol=first_unknown, message=f"'{first_unknown}' no es una operación conocida.")

    nouns = [(t, k) for t, k in kinds if k == "model"]
    selectors = [t for t, k in kinds if k == "selector"]
    relations = [(t, k) for t, k in kinds if k == "relation"]

    if not nouns:
        return SemanticError(symbol=verb, message=f"'{verb}' necesita un sustantivo (modelo) sobre el cual operar.")

    noun = nouns[0][0]
    ref: SExpr
    if selectors:
        ref = [Symbol("doc"), Symbol(noun), selectors[0]]
    else:
        ref = [Symbol("docs"), Symbol(noun)]

    if relations:
        ref = [Symbol("rel"), Symbol(relations[0][0]), ref]

    expr: SExpr = [Symbol(verb), ref]
    if projection:
        expr += [Keyword("project"), Symbol(projection)]
    return expr


def _split_projection(tokens: list[str]) -> tuple[list[str], str | None]:
    """Strip a trailing --<projection> flag."""
    words, projection = [], None
    for t in tokens:
        if t.startswith("--"):
            projection = t[2:]
        else:
            words.append(t)
    return words, projection
