"""The rule tools, level 2 (spec 14 §4, nivel 2): relation types declared and edited as
documents, by forms, in the session of `(world, speaker)`; an edit simulated first.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.mcp.tool_table import ToolTable
from pron.mcp.writes import Writes
from pron.world.mutability import RULES

if TYPE_CHECKING:
    from pron.mcp.app import McpApp

Answer = dict[str, Any]


class RuleTools:
    """kb_rule_declare, kb_rule_edit."""

    def __init__(self, app: McpApp) -> None:
        self.app = app

    def register(self, table: ToolTable) -> None:
        table.add("kb_rule_declare", self.kb_rule_declare, level=RULES)
        table.add("kb_rule_edit", self.kb_rule_edit, level=RULES)

    def writes(self, world: str, speaker: str | None) -> Writes:
        return Writes(self.app.mounts.session(world, speaker))

    def kb_rule_declare(
        self,
        world: str,
        name: str,
        source_types: list[str],
        target_types: list[str],
        cardinality: str,
        description: str,
        direction: str | None = None,
        axis: str | None = None,
        condition: str | None = None,
        speaker: str | None = None,
        dry_run: bool = False,
    ) -> Answer:
        """Declare a relation type rt-<name>: which models it joins, its cardinality
        (one_to_one, one_to_many, many_to_one, many_to_many), axis and condition. Level 2."""
        w = self.writes(world, speaker)
        return w.rule_declare(
            name,
            source_types,
            target_types,
            cardinality,
            description,
            direction,
            axis,
            condition,
            dry_run,
        )

    def kb_rule_edit(
        self,
        world: str,
        name: str,
        changes: dict[str, Any],
        confirm: bool = False,
        speaker: str | None = None,
        dry_run: bool = False,
    ) -> Answer:
        """Edit relation type rt-<name> ({field: value}). Simulated first: if existing edges
        would break it writes nothing and answers them in `broken`; confirm: true writes
        anyway. Level 2."""
        return self.writes(world, speaker).rule_edit(name, changes, confirm, dry_run)
