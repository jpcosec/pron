"""pron documents itself from its code (spec 08 step 9): a CliCommandDoc per `_cmd_*`
handler, from its docstring and its argparse arguments, and a SurfaceDoc per public
module, from its module docstring. Both are sldb models shipped by sldb.
"""

from __future__ import annotations

import ast
import importlib
import inspect
from pathlib import Path
from typing import Any

from pron.world import World

PACKAGE = Path(__file__).parent
TAGS = ["system:pron", "domain:system_architecture", "kind:software", "impl:here", "entity:cli_command"]
SURFACE_TAGS = ["system:pron", "domain:system_architecture", "kind:software", "impl:here", "entity:module"]
MODULES = ["world", "store", "graph", "lexicon", "embedder", "resolve", "verbs", "kernel", "dialogue", "ledger", "display", "session",
           "docs", "lints", "migrate", "surface.tokens", "surface.dates", "surface.nouns", "surface.interpret", "cli.main", "cli.repl"]


def _parse_doc(doc: str) -> tuple[str, str, str]:
    """synopsis (first line), how it works (paragraphs before Usage), usage block."""
    lines = (doc or "").strip().splitlines()
    synopsis = lines[0].strip() if lines else ""
    rest = "\n".join(lines[1:]).strip()
    how, _, usage = rest.partition("Usage:")
    return synopsis, how.strip(), usage.strip()


def command_specs() -> list[dict[str, Any]]:
    from pron.cli.main import build_parser
    main = importlib.import_module("pron.cli.main")
    parser = build_parser()
    subparsers = next(a for a in parser._actions if isinstance(a, __import__("argparse")._SubParsersAction))
    specs = []
    for name, sub in subparsers.choices.items():
        fn = sub.get_default("fn")
        synopsis, how, usage = _parse_doc(fn.__doc__ or "")
        args = []
        for a in sub._actions:
            if a.dest in ("help", "fn"):
                continue
            flag = a.option_strings[0] if a.option_strings else a.dest
            args.append(f"{flag} | {'required' if a.required or not a.option_strings else 'optional'} | {a.help or ''}")
        specs.append({
            "id": f"cmd-pron-{name}", "system": "pron", "command_path": name, "synopsis": synopsis or sub.description or "",
            "purpose": synopsis, "how_it_works": how or synopsis, "arguments": "\n".join(args) or "(none)", "usage": usage or f"pron {name}",
            "tags": TAGS, "provenance": f"src/pron/cli/main.py:{fn.__name__}",
        })
    return specs


def surface_specs() -> list[dict[str, Any]]:
    specs = []
    for mod in MODULES:
        module = importlib.import_module(f"pron.{mod}")
        doc = (module.__doc__ or "").strip()
        first, _, rest = doc.partition("\n\n")
        tree = ast.parse(inspect.getsource(module))
        names = [n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and not n.name.startswith("_")]
        specs.append({
            "id": f"surface-pron-{mod.replace('.', '-')}", "system": "pron", "surface": mod, "purpose": first or mod,
            "how_it_works": rest.strip() or first, "commands": "\n".join(names) or "(none)", "tags": SURFACE_TAGS,
            "provenance": f"src/pron/{mod.replace('.', '/')}.py",
        })
    return specs


def synchronize_docs(world: World, check: bool = False) -> list[str]:
    """Create or update the command and surface documents of pron's own world. Returns what changed
    (or, with check, what would change)."""
    store = world.store
    changed: list[str] = []
    for ref in ("sldb.models.knowledge_surface:CliCommandDoc", "sldb.models.knowledge_surface:SurfaceDoc"):
        if ref.split(":")[1] not in world.model_names():
            if check:
                changed.append(f"model {ref} not registered")
            else:
                store.register_model(ref)
    from sldb.runtime.validation import extract_model_data, render_model_markdown

    for model, specs, folder in (("CliCommandDoc", command_specs(), "commands"), ("SurfaceDoc", surface_specs(), "surfaces")):
        model_type = store.model_type(model) if model in world.model_names() else None
        for spec in specs:
            existing = store.doc(model, spec["id"])
            # compare in the document's canonical form: what the template renders and extracts back
            canonical = extract_model_data(model_type, render_model_markdown(model_type, spec)) if model_type else spec
            if existing is not None and {k: existing.payload.get(k) for k in canonical} == canonical:
                continue
            changed.append(f"{model} {spec['id']}")
            if check:
                continue
            if existing is not None:
                store.untrack(spec["id"])
            store.create(model, spec["id"], spec, world.root / "knowledge" / folder / f"{spec['id']}.md")
    return changed
