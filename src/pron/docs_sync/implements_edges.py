"""The implements edges of pron's knowledge base (spec 08 step 9, spec 03): one RelationDoc
per (module or command, chapter its docstring cites); an edge no docstring cites anymore goes.
"""

from __future__ import annotations

from typing import Any

from pron.world.world import World

Plan = tuple[str, list[dict[str, Any]], Any]


class ImplementsEdges:
    """Brings one world's implements edges in line with the docstrings' citations."""

    def __init__(self, world: World, check: bool) -> None:
        self.world = world
        self.store = world.store
        self.check = check

    def __call__(self, plans: list[Plan]) -> list[str]:
        """`plans[0]` holds the SpecDocs; the rest, the documents that cite them."""
        if (
            "RelationDoc" not in self.world.model_names()
            or self.store.doc("RelationTypeDoc", "rt-implements") is None
        ):
            return ["relation type implements not declared: run pron init --knowledge"]
        wanted = self._wanted(plans)
        existing = {
            d.name
            for d in self.store.docs_of("RelationDoc")
            if d.payload.get("relation_type") == "implements"
        }
        changed = [
            self._add(name, src, tgt)
            for name, (src, tgt) in wanted.items()
            if name not in existing
        ]
        for name in sorted(existing - set(wanted)):
            changed.append(f"RelationDoc {name} (stale)")
            if not self.check:
                self.store.untrack(name)
        return changed

    @staticmethod
    def _wanted(plans: list[Plan]) -> dict[str, tuple[str, str]]:
        """edge name -> (source, target), for every cite that names a known chapter."""
        chapters = {s["_chapter"]: s["id"] for s in plans[0][1]}
        wanted: dict[str, tuple[str, str]] = {}
        for model, specs, _ in plans[1:]:
            for spec in specs:
                for cite in spec.get("_cites", []):
                    target = chapters.get(cite.lower())
                    if target:
                        src, tgt = f"{model}:{spec['id']}", f"SpecDoc:{target}"
                        wanted[f"implements--{src}--{tgt}"] = (src, tgt)
        return wanted

    def _add(self, name: str, src: str, tgt: str) -> str:
        if not self.check:
            self.store.create(
                "RelationDoc",
                name,
                {
                    "title": name,
                    "source_id": src,
                    "target_id": tgt,
                    "relation_type": "implements",
                    "condition": "",
                    "notes": "derived from the docstring",
                },
                self.world.root / "knowledge" / "relations" / f"{name}.md",
            )
        return f"RelationDoc {name}"
