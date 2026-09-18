"""`kb_model_extend` (spec 14 §4, nivel 3): a registered model edited through its draft —
`model_fields_add`, `model_fields_remove`, `model_template_edit`, `model_validate_draft` —
and, with `confirm`, `model_promote`. Without `confirm` it answers the draft and its
validation and leaves the draft as it found it. No MoveDoc and no undo (spec 12 §4).
"""

from __future__ import annotations

from typing import Any

from pron.mcp.schema.draft_file import DraftFile
from pron.mcp.schema.field_decl import FieldDecl
from pron.mcp.writes.arg_error import ArgError
from pron.world.store_error import StoreError
from pron.world.world import World


class ModelExtend:
    """One world's registered models, edited by draft."""

    def __init__(self, world: World) -> None:
        self.world, self.store = world, world.store

    def __call__(
        self,
        name: str,
        add_fields: list | None = None,
        remove_fields: list[str] | None = None,
        template: str | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if name not in self.store.model_names():
            return _error(f"model {name} is not registered")
        draft = DraftFile(self.store, name)
        try:
            self._edit(name, add_fields or [], remove_fields or [], template)
            plan = {
                "draft": draft.text(),
                "validation": self.store.model_validate_draft(name),
            }
        except (ArgError, StoreError) as exc:
            draft.restore()
            return _error(f"the draft of {name} does not validate: {exc}")
        if not confirm:
            draft.restore()
            return {
                "text": f"Would change model {name}. Send confirm: true to promote it.",
                "outcome": "preview",
                "written": False,
                **plan,
            }
        return {**plan, **self._promote(name, draft)}

    def _edit(
        self, name: str, add: list, remove: list[str], template: str | None
    ) -> None:
        decls = [FieldDecl.of(f) for f in add]
        if not decls and not remove and template is None:
            raise ArgError(
                "nothing to change: give add_fields, remove_fields or template"
            )
        for d in decls:
            self.store.model_fields_add(
                name, d.name, d.annotation, d.description, d.default_json()
            )
        for field in remove:
            self.store.model_fields_remove(name, str(field))
        if template is not None:
            self.store.model_template_edit(name, template)

    def _promote(self, name: str, draft: DraftFile) -> dict[str, Any]:
        try:
            report = self.store.model_promote(name)
        except StoreError as exc:
            draft.restore()
            return _error(f"{name} was not promoted: {exc}")
        self.world.refresh()
        return {
            "text": f"Promoted model {name} (version {report.get('version')}).",
            "outcome": "unico",
            "written": True,
            "promoted": report,
        }


def _error(text: str) -> dict[str, Any]:
    return {"text": text, "outcome": "error", "written": False}
