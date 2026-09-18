"""The forms of the level-1 write tools (spec 14 §4, nivel 1): documents and edges. Each
method takes a tool's JSON arguments and returns the form text `session.eval` reads.
"""

from __future__ import annotations

from typing import Any

from pron.kernel.sexp.read_write import Sym, write
from pron.mcp.writes.arg_error import ArgError
from pron.mcp.writes.form_values import doc, symbol, value

# an edit op, the form verb it is, and whether its value is required, optional or absent
OPS = {
    "set": ("change", "required"),
    "add": ("add", "required"),
    "remove": ("remove", "optional"),
    "clean": ("clean", "absent"),
}


class ContentForms:
    """`kb_doc_create`, `kb_doc_edit`, `kb_doc_forget`, `kb_edge_assert`, `kb_edge_expire`
    and `kb_undo`, compiled."""

    @staticmethod
    def doc_create(model: str, fields: dict[str, Any], name: str | None = None) -> str:
        """`(create Model (as "name") (field value) …)`."""
        if not isinstance(fields, dict):
            raise ArgError("fields is an object of field → value")
        named = [[Sym("as"), name]] if name else []
        pairs = [[symbol(k, "field"), value(v)] for k, v in fields.items()]
        return write([Sym("create"), symbol(model, "model"), *named, *pairs])

    @staticmethod
    def doc_edit(export_id: str, ops: list[dict[str, Any]]) -> str:
        """`(move (change (doc "id") field value) (add …) (remove …) (clean …))`: one move."""
        if not isinstance(ops, list) or not ops:
            raise ArgError("ops is a non-empty list of {op, field, value?}")
        return write([Sym("move"), *(ContentForms.op(export_id, o) for o in ops)])

    @staticmethod
    def op(export_id: str, op: dict[str, Any]) -> list[Any]:
        """One `{op: set|add|remove|clean, field, value?}` as its form."""
        verb, arity = OPS.get(op.get("op", ""), ("", ""))
        if not verb:
            raise ArgError(f"op must be one of {', '.join(OPS)}, got {op.get('op')!r}")
        has = "value" in op
        if (arity == "required" and not has) or (arity == "absent" and has):
            raise ArgError(f"op {op['op']} takes {arity} value")
        tail = [value(op["value"])] if has else []
        return [Sym(verb), doc(export_id), symbol(op.get("field"), "field"), *tail]

    @staticmethod
    def doc_forget(export_id: str) -> str:
        return write([Sym("forget"), doc(export_id)])

    @staticmethod
    def edge_assert(source: str, relation: str, target: str) -> str:
        """`(assert relation (doc "source") (doc "target"))`."""
        rel = symbol(relation, "relation")
        return write([Sym("assert"), rel, doc(source), doc(target)])

    @staticmethod
    def edge_expire(relation_doc: str) -> str:
        """`(forget (doc "RelationDoc:…"))`: negating an edge is untracking its RelationDoc
        (spec 03); its id comes from `EdgeIds`."""
        return write([Sym("forget"), doc(relation_doc)])

    @staticmethod
    def undo() -> str:
        return write([Sym("undo")])
