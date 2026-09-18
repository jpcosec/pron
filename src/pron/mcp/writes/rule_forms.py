"""The forms of the level-2 write tools (spec 14 §4, nivel 2): relation types are documents,
declared and edited with the same forms as any other. A type named `<name>` is the
RelationTypeDoc `rt-<name>`.
"""

from __future__ import annotations

from typing import Any

from pron.kernel.sexp.read_write import Sym, write
from pron.mcp.writes.arg_error import ArgError
from pron.mcp.writes.form_values import doc, symbol, value


class RuleForms:
    """`kb_rule_declare` and `kb_rule_edit`, compiled."""

    @staticmethod
    def rule_id(name: str) -> str:
        return f"RelationTypeDoc:rt-{symbol(name, 'relation')}"

    @staticmethod
    def rule_declare(name: str, fields: dict[str, Any]) -> str:
        """`(create RelationTypeDoc (as "rt-<name>") (title name) (name name) (field value) …)`:
        `fields` are the tool's other arguments, the ones given."""
        rel = str(symbol(name, "relation"))
        given = {"title": rel, "name": rel, **fields}
        pairs = [[symbol(k, "field"), value(v)] for k, v in given.items()]
        return write(
            [Sym("create"), Sym("RelationTypeDoc"), [Sym("as"), f"rt-{rel}"], *pairs]
        )

    @staticmethod
    def rule_edit(name: str, changes: dict[str, Any]) -> str:
        """`(move (change (doc "RelationTypeDoc:rt-<name>") field value) …)`. The name is
        not a change: its edges carry it, and renaming would leave them without a type."""
        if not isinstance(changes, dict) or not changes:
            raise ArgError("changes is a non-empty object of field → value")
        if "name" in changes:
            raise ArgError("a relation type is not renamed: declare a new one")
        ref = doc(RuleForms.rule_id(name))
        steps = [
            [Sym("change"), ref, symbol(k, "field"), value(v)]
            for k, v in changes.items()
        ]
        return write([Sym("move"), *steps])
