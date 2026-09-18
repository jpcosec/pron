"""The write tools of levels 1 and 2 (spec 14 §4): each one the `Writes` of the session of
`(world, speaker)`, its JSON arguments compiled to a form and evaluated there — or only
pre-validated with `dry_run`. `speaker` defaults to the server's.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.mcp.tool_table import ToolTable
from pron.mcp.writes import Writes
from pron.mcp.rule_tools import RuleTools
from pron.world.mutability import CONTENT

if TYPE_CHECKING:
    from pron.mcp.app import McpApp

LEVELS = {
    "kb_doc_create": CONTENT,
    "kb_doc_edit": CONTENT,
    "kb_doc_forget": CONTENT,
    "kb_edge_assert": CONTENT,
    "kb_edge_expire": CONTENT,
    "kb_undo": CONTENT,
}
Answer = dict[str, Any]


class WriteTools:
    """kb_doc_create, kb_doc_edit, kb_doc_forget, kb_edge_assert, kb_edge_expire, kb_undo;
    and the rule tools of level 2 with them."""

    def __init__(self, app: McpApp) -> None:
        self.app = app

    def register(self, table: ToolTable) -> None:
        for name, level in LEVELS.items():
            table.add(name, getattr(self, name), level=level)
        RuleTools(self.app).register(table)

    def writes(self, world: str, speaker: str | None) -> Writes:
        return Writes(self.app.mounts.session(world, speaker))

    def kb_doc_create(
        self,
        world: str,
        model: str,
        fields: dict[str, Any],
        name: str | None = None,
        speaker: str | None = None,
        dry_run: bool = False,
    ) -> Answer:
        """Create a document of `model` from its fields (JSON; the model's template renders
        it): (create Model (as "name") (field value) …). Level 1."""
        return self.writes(world, speaker).doc_create(model, fields, name, dry_run)

    def kb_doc_edit(
        self,
        world: str,
        id: str,
        ops: list[dict[str, Any]],
        speaker: str | None = None,
        dry_run: bool = False,
    ) -> Answer:
        """Edit a document (Model:doc) in one move: ops is a list of {op: set|add|remove|clean,
        field, value?}. Sections of a document are fields too. Level 1."""
        return self.writes(world, speaker).doc_edit(id, ops, dry_run)

    def kb_doc_forget(
        self, world: str, id: str, speaker: str | None = None, dry_run: bool = False
    ) -> Answer:
        """Stop tracking a document (Model:doc): (forget (doc "id")). Level 1."""
        return self.writes(world, speaker).doc_forget(id, dry_run)

    def kb_edge_assert(
        self,
        world: str,
        source: str,
        relation: str,
        target: str,
        speaker: str | None = None,
        dry_run: bool = False,
    ) -> Answer:
        """Assert an edge source -relation-> target (ids Model:doc), checked against the
        relation type and its condition. Level 1."""
        return self.writes(world, speaker).edge_assert(
            source, relation, target, dry_run
        )

    def kb_edge_expire(
        self,
        world: str,
        source: str,
        relation: str,
        target: str,
        speaker: str | None = None,
        dry_run: bool = False,
    ) -> Answer:
        """Negate an edge: forget its RelationDoc; what it was stays in the ledger. Level 1."""
        return self.writes(world, speaker).edge_expire(
            source, relation, target, dry_run
        )

    def kb_undo(
        self, world: str, speaker: str | None = None, dry_run: bool = False
    ) -> Answer:
        """Undo this speaker's last move in the world: (undo). Level 1."""
        return self.writes(world, speaker).undo(dry_run)
