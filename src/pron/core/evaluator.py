"""Evaluator: resolves each symbol through its anchor and dispatches by kind.

Implements atom-knowledge-core-is-a-semantically-anchored-s-expression-evaluator.
Grounds (docs m), (doc m "sel"), (rel r expr) and dispatches operations.
"""
from __future__ import annotations

from typing import Any

from knowledge.bridges.kgdb_bridge import KgdbBridge
from knowledge.bridges.sldb_bridge import SldbBridge
from knowledge.core.anchors import Anchor, AnchorRegistry
from knowledge.core.resolution import resolve_noun
from knowledge.core.results import (
    Ambiguous, Missing, OperationResult, Resolved, SemanticError,
)
from knowledge.core.sexpr import Keyword, SExpr, Symbol, serialize
from knowledge.ops import read as read_ops


class Evaluator:
    """Evaluates Meaning against the world (sldb + kgdb)."""

    def __init__(self, sldb: SldbBridge, kgdb: KgdbBridge, registry: AnchorRegistry) -> None:
        self.sldb = sldb
        self.kgdb = kgdb
        self.registry = registry

    def eval(self, expr: SExpr):
        """Evaluate a full expression: (op arg* [:project sym])."""
        if not expr or not isinstance(expr[0], Symbol):
            return SemanticError(symbol=serialize(expr), message="la expresión no empieza con una operación.")
        anchor = self.registry.lookup(expr[0].name)
        if isinstance(anchor, SemanticError):
            return anchor
        if anchor.kind != "operation":
            return SemanticError(
                symbol=anchor.symbol,
                message=f"'{anchor.symbol}' no es una operación (es {anchor.kind}: {anchor.motive}).",
            )
        args, projection = self._split_options(expr[1:])
        grounded = [self._ground(a) for a in args]
        for g in grounded:
            if isinstance(g, (Ambiguous, Missing, SemanticError)):
                return g
        op_name = anchor.ref.removeprefix("op:")
        return self._dispatch(op_name, grounded, projection)

    def _split_options(self, args: list) -> tuple[list, Anchor | None]:
        """Trailing :project <symbol> pair -> projection anchor."""
        projection = None
        out = list(args)
        if len(out) >= 2 and isinstance(out[-2], Keyword) and out[-2].name == "project":
            sym = out[-1]
            anchor = self.registry.lookup(sym.name if isinstance(sym, Symbol) else str(sym))
            if isinstance(anchor, SemanticError):
                return out, None
            projection = anchor
            out = out[:-2]
        return out, projection

    def _ground(self, arg):
        """Ground one argument: refs become world values, literals pass through."""
        if not isinstance(arg, list) or not arg or not isinstance(arg[0], Symbol):
            return arg
        head = arg[0].name
        if head == "docs":
            return self._ground_docs(arg)
        if head == "doc":
            return self._ground_doc(arg)
        if head == "rel":
            return self._ground_rel(arg)
        return self.eval(arg)

    def _model_anchor(self, sym) -> Anchor | SemanticError:
        anchor = self.registry.lookup(sym.name if isinstance(sym, Symbol) else str(sym))
        if isinstance(anchor, SemanticError):
            return anchor
        if anchor.kind != "model":
            return SemanticError(symbol=anchor.symbol, message=f"'{anchor.symbol}' no es un model (es {anchor.kind}).")
        return anchor

    def _ground_docs(self, arg):
        anchor = self._model_anchor(arg[1])
        if isinstance(anchor, SemanticError):
            return anchor
        model = anchor.ref.removeprefix("model:")
        return {"kind": "docs", "model": model, "docs": self.sldb.documents_of_model(model)}

    def _ground_doc(self, arg):
        anchor = self._model_anchor(arg[1])
        if isinstance(anchor, SemanticError):
            return anchor
        model = anchor.ref.removeprefix("model:")
        selector = arg[2] if len(arg) > 2 else ""
        return resolve_noun(self.sldb, model, str(selector), anchor.motive)

    def _ground_rel(self, arg):
        anchor = self.registry.lookup(arg[1].name if isinstance(arg[1], Symbol) else str(arg[1]))
        if isinstance(anchor, SemanticError):
            return anchor
        if anchor.kind != "relation":
            return SemanticError(symbol=anchor.symbol, message=f"'{anchor.symbol}' no es una relation (es {anchor.kind}).")
        inner = self._ground(arg[2])
        if isinstance(inner, (Ambiguous, Missing, SemanticError)):
            return inner
        return {"kind": "rel", "anchor": anchor, "source": inner}

    def _dispatch(self, op: str, args: list, projection: Anchor | None):
        ops = {"check": read_ops.check, "next": read_ops.next_, "return": read_ops.return_}
        fn = ops.get(op)
        if fn is None:
            return SemanticError(symbol=op, message=f"operación 'op:{op}' aún no implementada.")
        return fn(self, args, projection)


def project_payload(payload: dict, projection: Anchor | None) -> dict:
    """Apply a fields:/view: projection to a payload."""
    if projection is None:
        return payload
    ref = projection.ref
    if ref.startswith("fields:"):
        wanted = ref.removeprefix("fields:").split(",")
        return {k: v for k, v in payload.items() if k in wanted}
    if ref == "view:summary":
        keep = ("id", "title", "name", "status")
        return {k: v for k, v in payload.items() if k in keep}
    return payload
