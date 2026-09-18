"""The level-2 write tools of one session (spec 14 §4, nivel 2): relation types declared and
edited as documents. An edit is simulated first (`RuleEffect`): if it would break edges it
does not write and answers them; with `confirm` it writes anyway and the answer brings them.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.mcp.writes.form_runner import FormRunner
from pron.mcp.writes.rule_effect import RuleEffect
from pron.mcp.writes.rule_forms import RuleForms
from pron.world.mutability import RULES

if TYPE_CHECKING:
    from pron.session import Session

Answer = dict[str, Any]


class RuleWrites:
    """`kb_rule_declare` and `kb_rule_edit`, as methods of the session they write in."""

    def __init__(self, session: Session):
        self.session = session
        self.runner = FormRunner(session)

    def rule_declare(
        self,
        name: str,
        source_types: list[str],
        target_types: list[str],
        cardinality: str,
        description: str,
        direction: str | None = None,
        axis: str | None = None,
        condition: str | None = None,
        dry_run: bool = False,
    ) -> Answer:
        optional = {"direction": direction, "axis": axis, "condition": condition}
        fields = {
            "source_types": source_types,
            "target_types": target_types,
            "cardinality": cardinality,
            **{k: v for k, v in optional.items() if v is not None},
            "description": description,
        }
        compile = lambda: RuleForms.rule_declare(name, fields)  # noqa: E731
        return self.runner(RULES, compile, dry_run)

    def rule_edit(
        self,
        name: str,
        changes: dict[str, Any],
        confirm: bool = False,
        dry_run: bool = False,
    ) -> Answer:
        refused = self.runner.ladder.requires(RULES)
        if refused is not None:
            return refused
        broken = self._broken(name, changes)
        if broken and not confirm:
            return _held(broken)
        answer = self.runner(RULES, lambda: RuleForms.rule_edit(name, changes), dry_run)
        return {**answer, "broken": broken}

    def _broken(self, name: str, changes: Any) -> list[dict[str, Any]]:
        """What the edit would break; nothing to judge when the changes make no edit (the
        compile then says why)."""
        if not isinstance(changes, dict):
            return []
        return RuleEffect(self.session)(name, changes)


def _held(broken: list[dict[str, Any]]) -> Answer:
    return {
        "text": f"This would break {len(broken)} edge(s); nothing was written. "
        "Send confirm: true to write it anyway.",
        "outcome": "error",
        "move_id": "",
        "writes": [],
        "broken": broken,
    }
