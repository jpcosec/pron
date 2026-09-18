"""`kb_audit` (spec 14 §4, Auditoría): what `pron check` says of a world plus `check_edges`
(the same as `_store/integrity`), and, when the server started with `--audit MODULE:FUNC`,
that function's report on the world's root: a world's own tests, unknown to pron. Level 0.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pron.mcp.tool_table import ToolTable
from pron.mcp.world_state import WorldState

if TYPE_CHECKING:
    from pron.mcp.app import McpApp


class AuditTool:
    """kb_audit."""

    def __init__(self, app: McpApp) -> None:
        self.app = app

    def register(self, table: ToolTable) -> None:
        table.add("kb_audit", self.kb_audit, level=0)

    def kb_audit(self, world: str) -> dict[str, Any]:
        """Audit a world: pron check's lints and the edge index's problems, and the
        server's --audit function's report on the world, when there is one."""
        mount = self.app.mounts[world]
        answer = WorldState(mount).integrity()
        if self.app.audit:
            answer["audit"] = self.external(
                str(mount.world.root), mount.world.store.pythonpath
            )
        return answer

    def external(self, root: str, pythonpath: str) -> dict[str, Any]:
        """FUNC(root) of --audit MODULE:FUNC, imported from the world's pythonpath."""
        module, _, func = str(self.app.audit).partition(":")
        if pythonpath and pythonpath not in sys.path:
            sys.path.insert(0, pythonpath)
        try:
            report = getattr(importlib.import_module(module), func)(Path(root))
        except Exception as exc:  # noqa: BLE001 - a failing audit is its report
            return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        return dict(report)
