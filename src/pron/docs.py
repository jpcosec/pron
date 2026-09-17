"""pron's own knowledge base is derived from this repo (spec 08 step 9): a CliCommandDoc
per command from its handler's docstring and its click parameters, a SurfaceDoc per
module from its module docstring, a SpecDoc per chapter of source/spec, the hand-written
ExplanationDocs of knowledge/explanations plus the ReadmeDoc that composes them into
README.md, and one `implements` edge from each module or command to every chapter its
docstring cites ("spec 06", "spec 11 §2"). Nothing is hand-kept except the explanations:
the docstrings and the README's declaration are the source.

Each kind of document is its own class in pron.docs_sync; `synchronize_docs` runs them in
order.
"""

from __future__ import annotations

from pron.docs_sync.command_docs import CommandDocs
from pron.docs_sync.generated_docs import GeneratedDocs
from pron.docs_sync.implements_edges import ImplementsEdges
from pron.docs_sync.readme_render import ReadmeRender
from pron.docs_sync.spec_docs import SpecDocs
from pron.docs_sync.stale_surfaces import StaleSurfaces
from pron.docs_sync.surface_docs import SurfaceDocs, discover_modules
from pron.docs_sync.written_docs import WrittenDocs
from pron.world.world import World

MODULES = discover_modules()


def synchronize_docs(world: World, check: bool = False) -> list[str]:
    """Create or update the documents of pron's own world. Returns what changed (or, with
    check, what would change)."""
    generated = GeneratedDocs(world, check)
    changed = generated.missing_models()
    if check and changed:
        return changed
    plans = [
        ("SpecDoc", SpecDocs(world.root)(), None),
        ("CliCommandDoc", CommandDocs()(), "knowledge/commands"),
        ("SurfaceDoc", SurfaceDocs(MODULES)(), "knowledge/surfaces"),
    ]
    for plan in plans:
        changed += generated(plan)
    changed += StaleSurfaces(world, check)(plans[2][1])
    changed += WrittenDocs(world, check)()
    changed += ReadmeRender(world, check)()
    changed += ImplementsEdges(world, check)(plans)
    return changed
