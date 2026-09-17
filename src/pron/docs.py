"""pron's own knowledge base is derived from this repo (spec 08 step 9): a CliCommandDoc
per command from its handler's docstring and its click parameters, a SurfaceDoc per
module from its module docstring, a SpecDoc per chapter of source/spec, the hand-written
ExplanationDocs of knowledge/explanations plus the ReadmeDoc that composes them into
README.md, and one `implements` edge from each module or command to every chapter its
docstring cites ("spec 06", "spec 11 §2"). Nothing is hand-kept except the explanations:
the docstrings and the README's declaration are the source.
"""

from __future__ import annotations

import ast
import importlib
import inspect
import os
import re
from pathlib import Path
from typing import Any

from pron.world.world import World

PACKAGE = Path(__file__).parent
TAGS = [
    "system:pron",
    "domain:system_architecture",
    "kind:software",
    "impl:here",
    "entity:cli_command",
]
SURFACE_TAGS = [
    "system:pron",
    "domain:system_architecture",
    "kind:software",
    "impl:here",
    "entity:module",
]
PACKAGE_DIR = Path(__file__).parent
EXPLANATIONS_DIR = Path("knowledge") / "explanations"
README_PATH = Path("knowledge") / "readme.md"
README_ID = "readme"
# documents written where they live, by hand or by a turn: (folder, model, id prefix)
WRITTEN_FOLDERS = [
    (EXPLANATIONS_DIR, "ExplanationDoc", ""),
    (Path("knowledge") / "anchors", "AnchorDoc", "anchor-"),
    (Path("knowledge") / "projections", "ProjectionDoc", "projection-"),
    (Path("ledger"), "MoveDoc", ""),
]


def _discover_modules() -> list[str]:
    """Every module of the package, minus dunders and private files, dotted."""
    return sorted(
        p.relative_to(PACKAGE_DIR).with_suffix("").as_posix().replace("/", ".")
        for p in PACKAGE_DIR.rglob("*.py")
        if not p.stem.startswith("_")
    )


MODULES = _discover_modules()
SPEC_DIR = Path("source") / "spec"
SPEC_REF = re.compile(r"\bspec\s+(\d{2}[a-z]?)\b", re.I)


def _parse_doc(doc: str) -> tuple[str, str, str]:
    """synopsis (first line), how it works (paragraphs before Usage), usage block."""
    lines = (doc or "").strip().splitlines()
    synopsis = lines[0].strip() if lines else ""
    rest = "\n".join(lines[1:]).strip()
    how, _, usage = rest.partition("Usage:")
    return synopsis, how.strip(), usage.strip()


def command_specs() -> list[dict[str, Any]]:
    """A CliCommandDoc payload per command of pron's click group, in the order they were added."""
    from pron.cli.main import cli

    return [_command_spec(name, command) for name, command in cli.commands.items()]


def _command_spec(name: str, command) -> dict[str, Any]:
    fn = command.callback
    synopsis, how, usage = _parse_doc(fn.__doc__ or "")
    args = [_argument_line(param) for param in command.params]
    return {
        "id": f"cmd-pron-{name}",
        "system": "pron",
        "command_path": name,
        "synopsis": synopsis or command.help or "",
        "purpose": synopsis,
        "how_it_works": how or synopsis,
        "arguments": "\n".join(args) or "(none)",
        "usage": usage or f"pron {name}",
        "tags": TAGS,
        "provenance": f"src/{fn.__module__.replace('.', '/')}.py:{fn.__name__}",
        "_cites": sorted(set(SPEC_REF.findall(fn.__doc__ or ""))),
    }


def _argument_line(param) -> str:
    """`<flag> | required|optional | <help>`; a positional counts as required even when it may be
    omitted, as the documents have always said."""
    import click

    positional = isinstance(param, click.Argument)
    flag = param.name if positional else param.opts[0]
    required = "required" if param.required or positional else "optional"
    return f"{flag} | {required} | {getattr(param, 'help', None) or ''}"


def surface_specs() -> list[dict[str, Any]]:
    specs = []
    for mod in MODULES:
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
        specs.append(
            {
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
        )
    return specs


def spec_specs(root: Path) -> list[dict[str, Any]]:
    """A SpecDoc per chapter file NN-….md of source/spec, tracked where it lives."""
    specs = []
    for path in sorted((root / SPEC_DIR).glob("[0-9][0-9]*.md")):
        text = path.read_text(encoding="utf-8").strip()
        first, _, body = text.partition("\n")
        chapter = path.stem.split("-", 1)[0]
        specs.append(
            {
                "id": f"spec-{chapter}",
                "title": first.lstrip("# ").strip(),
                "body": body.strip(),
                "_path": path,
                "_chapter": chapter.lower(),
            }
        )
    return specs


def synchronize_docs(world: World, check: bool = False) -> list[str]:
    """Create or update the documents of pron's own world. Returns what changed (or, with
    check, what would change)."""
    from sldb.runtime.validation import extract_model_data, render_model_markdown

    store = world.store
    changed: list[str] = []
    needed = {
        "CliCommandDoc": "sldb.models.knowledge_surface:CliCommandDoc",
        "SurfaceDoc": "sldb.models.knowledge_surface:SurfaceDoc",
        "SpecDoc": "pron.models:SpecDoc",
        "ExplanationDoc": "pron.models:ExplanationDoc",
        "ReadmeDoc": "pron.models:ReadmeDoc",
    }
    for model, ref in needed.items():
        if model not in world.model_names():
            if check:
                changed.append(f"model {ref} not registered")
            else:
                store.register_model(ref)
    if check and changed:
        return changed
    chapters = spec_specs(world.root)
    plans = [
        ("SpecDoc", chapters, None),
        ("CliCommandDoc", command_specs(), "knowledge/commands"),
        ("SurfaceDoc", surface_specs(), "knowledge/surfaces"),
    ]
    for model, specs, folder in plans:
        model_type = store.model_type(model)
        for spec in specs:
            payload = {k: v for k, v in spec.items() if not k.startswith("_")}
            existing = store.doc(model, spec["id"])
            canonical = extract_model_data(
                model_type, render_model_markdown(model_type, payload)
            )
            if (
                existing is not None
                and {k: existing.payload.get(k) for k in canonical} == canonical
            ):
                continue
            changed.append(f"{model} {spec['id']}")
            if check:
                continue
            if existing is not None:
                store.untrack(spec["id"])
            if folder is None:
                store.track(spec["_path"], model, spec["id"])
            else:
                store.create(
                    model, spec["id"], payload, world.root / folder / f"{spec['id']}.md"
                )
    changed += _stale_surfaces(world, plans[2][1], check)
    changed += _hand_written(world, check)
    changed += _render_readme(world, check)
    changed += _implements_edges(world, plans, check)
    return changed


def _stale_surfaces(world: World, specs, check: bool) -> list[str]:
    """A SurfaceDoc whose module no longer exists goes: untracked, and the file generated for
    it under knowledge/surfaces deleted. With check, report the drift and write nothing."""
    store = world.store
    wanted = {spec["id"] for spec in specs}
    stale = sorted(d.name for d in store.docs_of("SurfaceDoc") if d.name not in wanted)
    generated = (world.root / "knowledge" / "surfaces").resolve()
    for name in [] if check else stale:
        path = store.doc_path("SurfaceDoc", name)
        store.untrack(name)
        if path is not None and path.resolve().parent == generated:
            path.unlink(missing_ok=True)
    return [f"SurfaceDoc {name} (stale)" for name in stale]


def _hand_written(world: World, check: bool) -> list[str]:
    """The documents written where they live — explanations, anchors, projections, the
    moves of the ledger (spec 07) and the ReadmeDoc — are tracked from their files like the
    spec chapters; one is re-tracked when its payload changed. This is what lets the whole
    store be rebuilt from the repo (spec 08 step 9)."""
    changed = []
    for model, doc_id, path in _written_documents(world.root):
        if _retrack(world.store, model, doc_id, path, check):
            changed.append(f"{model} {doc_id}")
    return changed


def _written_documents(root: Path) -> list[tuple[str, str, Path]]:
    written = [
        (model, f"{prefix}{path.stem}", path)
        for folder, model, prefix in WRITTEN_FOLDERS
        for path in sorted((root / folder).glob("*.md"))
    ]
    if (root / README_PATH).is_file():
        written.append(("ReadmeDoc", README_ID, root / README_PATH))
    return written


def _retrack(store, model: str, doc_id: str, path: Path, check: bool) -> bool:
    """Whether the document drifted from its file; unless checking, track it again."""
    from sldb.runtime.validation import extract_model_data

    existing = store.doc(model, doc_id)
    canonical = extract_model_data(store.model_type(model), path.read_text(encoding="utf-8"))
    if existing is not None and {k: existing.payload.get(k) for k in canonical} == canonical:
        return False
    if not check:
        if existing is not None:
            store.untrack(doc_id)
        store.track(path, model, doc_id)
    return True


def _render_readme(world: World, check: bool) -> list[str]:
    """README.md at the repo root is the ReadmeDoc rendered, never edited by hand: the
    parts are composed by address. With check, report the drift and write nothing."""
    store = world.store
    doc = store.doc("ReadmeDoc", README_ID)
    if doc is None:
        return []
    from sldb.runtime.validation import render_model_markdown

    readme = world.root / "README.md"
    cwd = Path.cwd()
    try:
        os.chdir(world.root)  # composition child paths resolve from the process cwd
        rendered = render_model_markdown(store.model_type("ReadmeDoc"), dict(doc.payload))
    finally:
        os.chdir(cwd)
    rendered = re.sub(r"\n{3,}", "\n\n", rendered)  # the dropped parts list leaves a hole
    if not rendered.endswith("\n"):
        rendered += "\n"
    current = readme.read_text(encoding="utf-8") if readme.exists() else ""
    if current == rendered:
        return []
    changed = ["README.md out of date"]
    if not check:
        readme.write_text(rendered, encoding="utf-8")
    return changed


def _implements_edges(world: World, plans, check: bool) -> list[str]:
    """One implements edge per (module or command, chapter cited in its docstring); stale ones go."""
    store = world.store
    if (
        "RelationDoc" not in world.model_names()
        or store.doc("RelationTypeDoc", "rt-implements") is None
    ):
        return ["relation type implements not declared: run pron init --knowledge"]
    chapters = {s["_chapter"]: s["id"] for s in plans[0][1]}
    wanted: dict[str, tuple[str, str]] = {}
    for model, specs, _ in plans[1:]:
        for spec in specs:
            for cite in spec.get("_cites", []):
                target = chapters.get(cite.lower())
                if target:
                    src, tgt = f"{model}:{spec['id']}", f"SpecDoc:{target}"
                    wanted[f"implements--{src}--{tgt}"] = (src, tgt)
    changed = []
    existing = {
        d.name
        for d in store.docs_of("RelationDoc")
        if d.payload.get("relation_type") == "implements"
    }
    for name, (src, tgt) in wanted.items():
        if name in existing:
            continue
        changed.append(f"RelationDoc {name}")
        if not check:
            store.create(
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
                world.root / "knowledge" / "relations" / f"{name}.md",
            )
    for name in sorted(existing - set(wanted)):
        changed.append(f"RelationDoc {name} (stale)")
        if not check:
            store.untrack(name)
    return changed
