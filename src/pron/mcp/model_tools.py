"""The model tools, level 3 (spec 14 §4, nivel 3): `kb_model_create` and `kb_model_extend`.
The only writes below the forms, so both answer a preview and write nothing without
`confirm: true`. A new or changed model enters the world at once; the world's open sessions
are dropped so the next one opens over it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.mcp.schema.model_create import ModelCreate
from pron.mcp.schema.model_extend import ModelExtend
from pron.mcp.tool_table import ToolTable
from pron.world.mutability import MODELS

if TYPE_CHECKING:
    from pron.mcp.app import McpApp


class ModelTools:
    """kb_model_create, kb_model_extend."""

    def __init__(self, app: McpApp) -> None:
        self.app = app

    def register(self, table: ToolTable) -> None:
        table.add("kb_model_create", self.kb_model_create, level=MODELS)
        table.add("kb_model_extend", self.kb_model_extend, level=MODELS)

    def kb_model_create(
        self,
        world: str,
        name: str,
        fields: list[dict[str, Any]],
        template: str | None = None,
        base: str | None = None,
        confirm: bool = False,
        speaker: str | None = None,
    ) -> dict[str, Any]:
        """Generate a model (a StructuredNLDoc module under the server's pythonpath) from
        fields [{name, type: str|int|float|bool|list[str]|Literal[…], description,
        required?, default?, enum?}], with `template` or one section per field, optionally
        extending the registered model `base`, and register it. Without confirm: the module
        and its check, nothing written. Level 3; no undo."""
        answer = ModelCreate(self.app.mounts[world].world, world)(
            name, fields, template, base, confirm
        )
        return self._settled(world, answer)

    def kb_model_extend(
        self,
        world: str,
        name: str,
        add_fields: list[dict[str, Any]] | None = None,
        remove_fields: list[str] | None = None,
        template: str | None = None,
        confirm: bool = False,
        speaker: str | None = None,
    ) -> dict[str, Any]:
        """Edit a registered model through its draft: add fields (as in kb_model_create),
        remove fields, replace the template; validated against every document. Without
        confirm: the draft and its validation, nothing written; with it, promoted. Level 3;
        no undo."""
        answer = ModelExtend(self.app.mounts[world].world)(
            name, add_fields, remove_fields, template, confirm
        )
        return self._settled(world, answer)

    def _settled(self, world: str, answer: dict[str, Any]) -> dict[str, Any]:
        if answer.get("written"):
            self.app.mounts.forget_sessions(world)
        return answer
