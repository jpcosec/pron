"""A SurfaceDoc per module of pron (spec 08 step 9): its purpose and how it works from the
module docstring, its public top-level names, and the spec chapters the docstring cites.
Dunder and private files are not modules of the surface.
"""

from __future__ import annotations

import ast
import importlib
import inspect
from pathlib import Path
from typing import Any

from pron.docs_sync.command_docs import SPEC_REF

PACKAGE_DIR = Path(__file__).parent.parent
SURFACE_TAGS = [
    "system:pron",
    "domain:system_architecture",
    "kind:software",
    "impl:here",
    "entity:module",
]


def discover_modules() -> list[str]:
    """Every module of the package, minus dunders and private files, dotted."""
    return sorted(
        p.relative_to(PACKAGE_DIR).with_suffix("").as_posix().replace("/", ".")
        for p in PACKAGE_DIR.rglob("*.py")
        if not p.stem.startswith("_")
    )


class SurfaceDocs:
    """The SurfaceDoc payloads of the given modules (dotted, under pron)."""

    def __init__(self, modules: list[str]) -> None:
        self.modules = modules

    def __call__(self) -> list[dict[str, Any]]:
        return [self._spec(mod) for mod in self.modules]

    @staticmethod
    def _spec(mod: str) -> dict[str, Any]:
        module = importlib.import_module(f"pron.{mod}")
        doc = (module.__doc__ or "").strip()
        first, _, rest = doc.partition("\n\n")
        tree = ast.parse(inspect.getsource(module))
        names = [
            n.name
            for n in tree.body
            if isinstance(n, (ast.FunctionDef, ast.ClassDef))
            and not n.name.startswith("_")
        ]
        return {
            "id": f"surface-pron-{mod.replace('.', '-')}",
            "system": "pron",
            "surface": mod,
            "purpose": first or mod,
            "how_it_works": rest.strip() or first,
            "commands": "\n".join(names) or "(none)",
            "tags": SURFACE_TAGS,
            "provenance": f"src/pron/{mod.replace('.', '/')}.py",
            "_cites": sorted(set(SPEC_REF.findall(doc))),
        }
