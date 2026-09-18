"""The write tools of the MCP surface as a library (spec 14 §4, §5): their JSON arguments
compiled to forms (spec 13), evaluated in a `Session` — or only pre-validated with `dry_run`
(11 §7) — and answered as JSON; the ladder of mutability at their door; and the simulated
effect that guards an edit of a relation type. No MCP SDK here: the wiring to tools holds a
`Writes` per session and calls it.
"""

from __future__ import annotations

from pron.mcp.writes.arg_error import ArgError
from pron.mcp.writes.content_forms import ContentForms
from pron.mcp.writes.edge_ids import EdgeIds
from pron.mcp.writes.ladder import Ladder
from pron.mcp.writes.rule_effect import RuleEffect
from pron.mcp.writes.rule_forms import RuleForms
from pron.mcp.writes.writes import Writes

__all__ = [
    "ArgError",
    "ContentForms",
    "EdgeIds",
    "Ladder",
    "RuleEffect",
    "RuleForms",
    "Writes",
]
