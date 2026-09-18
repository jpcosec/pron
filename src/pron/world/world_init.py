"""Making a store a pron world (spec 01, spec 08 step 9): sldb's typed relations plus pron's
own models, the ledger and derived folders, and, for pron's own knowledge base, SpecDoc and
the relation type `implements`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pron.world.store import Store
from pron.world.world_template import WorldTemplate

PRON_MODELS = (
    "pron.models:AnchorDoc",
    "pron.models:ProjectionDoc",
    "pron.models:MoveDoc",
)
KNOWLEDGE_MODELS = (
    "pron.models:SpecDoc",
    "sldb.models.knowledge_surface:CliCommandDoc",
    "sldb.models.knowledge_surface:SurfaceDoc",
)
LEDGER_DIR = Path("ledger")
PROJECTIONS_DIR = Path("knowledge") / "projections"
KNOWLEDGE_RELATION_TYPES: list[dict[str, Any]] = [
    {
        "name": "implements",
        "axis": "HOW",
        "cardinality": "many_to_many",
        "source_types": ["SurfaceDoc", "CliCommandDoc"],
        "target_types": ["SpecDoc"],
        "description": "This module or command implements that chapter of the specification: the direct branch from the code to what it is supposed to do, derived from the spec references in the module's docstring.",
    },
]


class WorldInit:
    """Initializes one world's store; running it again adds only what is missing."""

    def __init__(self, root: str | Path, pythonpath: str | None = None) -> None:
        self.root = Path(root).resolve()
        self.pythonpath = pythonpath
        self.store = Store(self.root, pythonpath)

    def __call__(
        self, with_knowledge: bool = False, template: str | Path | None = None
    ) -> dict[str, Any]:
        from sldb.api import init_relations

        relations_report = init_relations(self.store.sp, self.store.pythonpath)
        refs = PRON_MODELS + (KNOWLEDGE_MODELS if with_knowledge else ())
        added = [ref for ref in refs if self.store.register_model(ref)]
        self._folders()
        types_added = self._knowledge_relation_types() if with_knowledge else []
        # a model registered without documents leaves its index hash behind until the next update
        self.store.update_index()
        from_template = (
            WorldTemplate(self.root, self.pythonpath)(template) if template else []
        )
        return {
            "relations": relations_report.summary(),
            "pron_models_added": added,
            "relation_types_added": types_added,
            "template_added": from_template,
        }

    def _folders(self) -> None:
        """The ledger, and .pron/ kept out of git."""
        (self.root / LEDGER_DIR).mkdir(exist_ok=True)
        (self.root / ".pron").mkdir(exist_ok=True)
        gitignore = self.root / ".pron" / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text("*\n", encoding="utf-8")

    def _knowledge_relation_types(self) -> list[str]:
        """The relation types pron's own knowledge base uses, declared as documents."""
        added = []
        for rt in KNOWLEDGE_RELATION_TYPES:
            name = f"rt-{rt['name']}"
            if self.store.doc("RelationTypeDoc", name) is not None:
                continue
            payload = {
                "title": rt["name"],
                "direction": "directed",
                "condition": "",
                **rt,
            }
            self.store.create(
                "RelationTypeDoc",
                name,
                payload,
                self.store.root
                / "knowledge"
                / "relations"
                / "types"
                / f"{rt['name']}.md",
            )
            added.append(rt["name"])
        return added


def init_world(
    root: str | Path,
    pythonpath: str | None = None,
    with_knowledge: bool = False,
    template: str | Path | None = None,
) -> dict[str, Any]:
    """Make a store a pron world: sldb's typed relations plus pron's own models. With
    with_knowledge, also what pron's own knowledge base needs: SpecDoc and the relation
    type `implements` (a module or command implements a spec chapter). With a template,
    the world is born with the words, projections and relation types the template holds."""
    return WorldInit(root, pythonpath)(with_knowledge, template)
