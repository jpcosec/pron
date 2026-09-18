"""The documents pron derives from its repo (spec 08 step 9): the models its knowledge base
needs, registered, and for each plan — SpecDocs tracked where the chapters live, CliCommandDocs
and SurfaceDocs written under knowledge/ — the documents that drifted, re-tracked or rewritten.
With check, nothing is written and the drift is reported.
"""

from __future__ import annotations

from typing import Any

from pron.docs_sync.doc_drift import drifted
from pron.world.doc_id import DocId
from pron.world.world import World

NEEDED_MODELS = {
    "CliCommandDoc": "sldb.models.knowledge_surface:CliCommandDoc",
    "SurfaceDoc": "sldb.models.knowledge_surface:SurfaceDoc",
    "SpecDoc": "pron.models:SpecDoc",
    "ExplanationDoc": "pron.models:ExplanationDoc",
    "ReadmeDoc": "pron.models:ReadmeDoc",
}

Plan = tuple[
    str, list[dict[str, Any]], "str | None"
]  # (model, payloads, folder or None: tracked in place)


class GeneratedDocs:
    """Brings one world's generated documents in line with their sources."""

    def __init__(self, world: World, check: bool) -> None:
        self.world = world
        self.store = world.store
        self.check = check

    def missing_models(self) -> list[str]:
        """The needed models not registered: registered now, or with check, reported."""
        changed: list[str] = []
        for model, ref in NEEDED_MODELS.items():
            if model not in self.world.model_names():
                if self.check:
                    changed.append(f"model {ref} not registered")
                else:
                    self.store.register_model(ref)
        return changed

    def __call__(self, plan: Plan) -> list[str]:
        from sldb.runtime.validation import extract_model_data, render_model_markdown

        model, specs, folder = plan
        model_type = self.store.model_type(model)
        changed: list[str] = []
        for spec in specs:
            payload = {k: v for k, v in spec.items() if not k.startswith("_")}
            existing = self.store.doc(DocId.of(model, spec["id"]))
            canonical = extract_model_data(
                model_type, render_model_markdown(model_type, payload)
            )
            if drifted(existing, canonical):
                changed.append(f"{model} {spec['id']}")
                self._write(model, spec, payload, folder, existing)
        return changed

    def _write(
        self,
        model: str,
        spec: dict[str, Any],
        payload: dict[str, Any],
        folder: str | None,
        existing: Any,
    ) -> None:
        if self.check:
            return
        doc_id = DocId.of(model, spec["id"])
        if existing is not None:
            self.store.untrack(doc_id)
        if folder is None:
            self.store.track(doc_id, spec["_path"])
        else:
            path = self.world.root / folder / f"{spec['id']}.md"
            self.store.create(doc_id, payload, path)
