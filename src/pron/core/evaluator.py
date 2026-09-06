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
        args, projection, where = self._split_options(expr[1:])
        grounded = [self._ground(a) for a in args]
        for g in grounded:
            if isinstance(g, (Ambiguous, Missing, SemanticError)):
                return g
        if where:
            grounded = [self._apply_where(g, where) for g in grounded]
        op_name = anchor.ref.removeprefix("op:")
        return self._dispatch(op_name, grounded, projection)

    def _apply_where(self, grounded, where: str):
        """Filter a docs set with sldb's real where engine."""
        if isinstance(grounded, dict) and grounded.get("kind") == "docs":
            return {**grounded, "docs": self.sldb.filter_where(grounded["docs"], where)}
        return grounded

    def _split_options(self, args: list) -> tuple[list, Anchor | None, str | None]:
        """Trailing :project <symbol> and :where "expr" pairs."""
        projection, where = None, None
        out = list(args)
        while len(out) >= 2 and isinstance(out[-2], Keyword):
            key, val = out[-2].name, out[-1]
            if key == "project":
                anchor = self.registry.lookup(val.name if isinstance(val, Symbol) else str(val))
                if not isinstance(anchor, SemanticError):
                    projection = anchor
            elif key == "where":
                where = str(val)
            else:
                break
            out = out[:-2]
        return out, projection, where

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
        if head in ("related", "common", "also"):
            return self._ground_setop(head, arg)
        if head == "filter-by":
            return self._ground_filter_by(arg)
        expanded = self._expand_macro(head, arg)
        if expanded is not None:
            return self._ground(expanded)
        return self.eval(arg)

    def _expand_macro(self, head: str, arg: list):
        """Expand a kind=expr anchor: substitute _ holes with the arguments.

        This is the derived-relation layer: a symbol whose referent is itself
        an s-expression over sldb+kgdb, declared as knowledge, not code.
        """
        anchor = self.registry.lookup(head)
        if isinstance(anchor, SemanticError) or anchor.kind != "expr":
            return None
        from knowledge.core.sexpr import parse
        template = parse(anchor.ref.removeprefix("expr:"))
        holes = iter(arg[1:])
        return _fill(template, holes)

    def _ground_setop(self, op: str, arg: list):
        """Set combinators over grounded node/doc sets.

        (related X)   -> everything one hop from X in the graph, any relation.
        (common X Y)  -> targets shared by X and Y (intersection of hops).
        (also X Y)    -> union of the grounded sets.
        """
        grounded = [self._ground(a) for a in arg[1:]]
        for g in grounded:
            if isinstance(g, (Ambiguous, Missing, SemanticError)):
                return g
        hops = [self._hop_targets(g) for g in grounded]
        for h in hops:
            if isinstance(h, SemanticError):
                return h
        if op == "related":
            ids = hops[0]
        elif op == "common":
            ids = set.intersection(*[set(h) for h in hops]) if hops else set()
        else:
            ids = set.union(*[set(h) for h in hops]) if hops else set()
        return {"kind": "nodes", "node_ids": sorted(ids)}

    def _ground_filter_by(self, arg: list):
        """(filter-by <model-sym> <field> <expr>) -> docs whose field equals the
        resolved doc's name. Joins by foreign-key field, a relation stored in
        neither kgdb (no edge) nor sldb (no query for it)."""
        if len(arg) != 4:
            return SemanticError(symbol="filter-by", message="filter-by requiere (filter-by modelo campo expr).")
        anchor = self._model_anchor(arg[1])
        if isinstance(anchor, SemanticError):
            return anchor
        field = arg[2].name if isinstance(arg[2], Symbol) else str(arg[2])
        inner = self._ground(arg[3])
        if isinstance(inner, (Ambiguous, Missing, SemanticError)):
            return inner
        if not isinstance(inner, Resolved):
            return SemanticError(symbol="filter-by", message="filter-by requiere un doc resuelto como valor.")
        model = anchor.ref.removeprefix("model:")
        docs = [d for d in self.sldb.documents_of_model(model)
                if str(d.payload.get(field, "")) == inner.name]
        return {"kind": "docs", "model": model, "docs": docs}

    def _hop_targets(self, grounded) -> list[str] | SemanticError:
        """All graph neighbors (out + in) of a grounded doc, any relation."""
        if not isinstance(grounded, Resolved):
            return SemanticError(symbol="related", message="los combinadores requieren docs resueltos.")
        if not self.kgdb.available():
            return SemanticError(symbol="related", message="no hay grafo; corre: knowledge project")
        nid = self.kgdb.document_node_id(grounded.model, grounded.name)
        out = [e["target_id"] for e in self.kgdb.edges_from(nid)]
        inc = self.kgdb.edges_to(nid)
        return sorted(set(out) | set(inc))

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


def _fill(item, holes):
    """Replace _ symbols in a template with successive arguments."""
    if isinstance(item, list):
        return [_fill(x, holes) for x in item]
    if isinstance(item, Symbol) and item.name == "_":
        try:
            return next(holes)
        except StopIteration:
            return item
    return item


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
