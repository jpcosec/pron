"""Describe public surfaces from source contracts; atom-pron-cli-and-modules-are-documented-from-source.

CliCommandDoc content comes from each command handler's own docstring in
cli/main.py (synopsis, how it works, and a trailing Usage: block), not a
parallel hand-maintained description — the same principle SurfaceDoc already
applies to every other module. Only the argument list is still hand-kept
here, since pron's CLI parses tokens by hand instead of through argparse.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from pydantic import JsonValue


@dataclass(frozen=True)
class DocumentSpec:
    model: str
    name: str
    folder: str
    payload: dict[str, JsonValue]


def describe_public_surfaces(
    root: Path, atoms: Mapping[str, str]
) -> tuple[DocumentSpec, ...]:
    """Derive command contracts and Python surfaces from the current source tree."""
    commands = _command_specs(root)
    surfaces = [
        _module_spec(path, root, atoms)
        for path in sorted((root / "src/pron").rglob("*.py"))
        if not path.name.startswith("__")
    ]
    return (*commands, *surfaces)


# name -> handler function in cli/main.py that implements it
_HANDLERS: dict[str, str] = {
    "anchors": "_cmd_anchors",
    "anchor add": "_cmd_anchor_add",
    "model add": "_cmd_model_add",
    "project": "_cmd_project",
    "docs": "_cmd_docs",
    "repl": "_cmd_repl",
    "eval": "_cmd_eval",
}

# irreducible without argparse: pron's CLI parses tokens by hand, so there is
# no parser object to introspect for flags the way kinesis does.
_ARGUMENTS: dict[str, str] = {
    "anchors": "[symbol] | optional | Filter to a single anchor symbol.\n--kb <root> | optional | KB root; defaults to the current working directory.\n--format json|text | optional | Output projection; defaults to json.",
    "anchor add": "<symbol> | required | The grammar symbol being declared.\n--kind model|expr|operation | required | The anchor's kind.\n--ref <typed-ref> | required | The referent, e.g. model:AtomDoc or 'expr:(related (doc atom _))'.\n--motive <text> | required | The semantic motive for the symbol.\n--kb <root> | optional | KB root; defaults to the current working directory.\n--format json|text | optional | Output projection; defaults to json.",
    "model add": "<module:Class> | required | The model reference to register, e.g. pron.bridges.write_models:FactDoc.\n--kb <root> | optional | KB root; defaults to the current working directory.",
    "project": "--kb <root> | optional | KB root; defaults to the current working directory.",
    "docs": "--check | optional | Verify instead of regenerating; exits non-zero on drift.\n--kb <root> | optional | KB root; defaults to the current working directory.",
    "repl": "--kb <root> | optional | KB root; defaults to the current working directory.\n--format json|text | optional | Output projection; defaults to text for repl (json everywhere else).",
    "eval": '<s-expr> | required | The s-expression to evaluate, e.g. \'(check (doc atom "x") :project title)\'.\n--kb <root> | optional | KB root; defaults to the current working directory.\n--format json|text | optional | Output projection; defaults to json.',
}


def _command_specs(root: Path) -> list[DocumentSpec]:
    tree = ast.parse((root / "src/pron/cli/main.py").read_text(encoding="utf-8"))
    docstrings = {
        node.name: ast.get_docstring(node) or ""
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }
    specs = []
    for name, handler in _HANDLERS.items():
        synopsis, how_it_works, usage = _parse_doc(docstrings[handler])
        identity = f"cmd-pron-{name.replace(' ', '-')}"
        specs.append(
            DocumentSpec(
                "CliCommandDoc",
                identity,
                "commands",
                {
                    "id": identity,
                    "system": "pron",
                    "command_path": f"pron {name}",
                    "synopsis": synopsis,
                    "purpose": synopsis,
                    "how_it_works": how_it_works,
                    "arguments": _ARGUMENTS[name],
                    "usage": usage,
                    "tags": [
                        "system:pron",
                        "domain:system_architecture",
                        "kind:software",
                        "impl:here",
                    ],
                    "provenance": f"src/pron/cli/main.py:{handler}",
                },
            )
        )
    return specs


def _parse_doc(doc: str) -> tuple[str, str, str]:
    """Split a handler's docstring into (synopsis, how_it_works, usage).

    The first paragraph is the synopsis; a trailing paragraph starting with
    'Usage:' becomes the usage block (its indentation preserved by
    ast.get_docstring's cleaning, then stripped back per line); everything
    in between is how_it_works.
    """
    paragraphs = [p for p in doc.strip().split("\n\n") if p.strip()]
    synopsis = paragraphs[0].strip() if paragraphs else ""
    body = paragraphs[1:]
    usage = ""
    if body and body[-1].lstrip().startswith("Usage:"):
        _, _, rest = body.pop().partition("Usage:")
        usage = "\n".join(line.strip() for line in rest.strip().splitlines())
    how_it_works = "\n\n".join(p.strip() for p in body) or synopsis
    return synopsis, how_it_works, usage


def _module_spec(path: Path, root: Path, atoms: Mapping[str, str]) -> DocumentSpec:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    docstring = ast.get_docstring(tree) or ""
    references = re.findall(r"atom-[a-z0-9-]+", docstring)
    module = ".".join(path.relative_to(root / "src").with_suffix("").parts)
    identity = "surface-" + module.replace(".", "-").replace("_", "-")
    commands = []
    for item in tree.body:
        if isinstance(item, ast.FunctionDef) and not item.name.startswith("_"):
            commands.append(_function_summary(item))
        if isinstance(item, ast.ClassDef) and not item.name.startswith("_"):
            fields = [
                ast.unparse(field)
                for field in item.body
                if isinstance(field, ast.AnnAssign)
                and isinstance(field.target, ast.Name)
                and not field.target.id.startswith("_")
            ]
            commands.append(item.name + (": " + "; ".join(fields) if fields else ""))
            commands.extend(
                f"{item.name}.{_function_summary(method)}"
                for method in item.body
                if isinstance(method, ast.FunctionDef)
                and not method.name.startswith("_")
            )
    return DocumentSpec(
        "SurfaceDoc",
        identity,
        "surfaces",
        {
            "id": identity,
            "system": "pron",
            "surface": module,
            "purpose": docstring.split(".")[0].split(";")[0].rstrip("."),
            "how_it_works": "\n\n".join(
                f"{reference}: {atoms[reference]}"
                for reference in references
                if reference in atoms
            ),
            "commands": "\n".join(commands)
            or "No public functions or classes at module scope.",
            "tags": [
                "system:pron",
                "domain:system_architecture",
                "kind:software",
                "impl:here",
            ],
            "provenance": str(path.relative_to(root)),
        },
    )


def _function_summary(function: ast.FunctionDef) -> str:
    result = f" -> {ast.unparse(function.returns)}" if function.returns else ""
    return f"{function.name}({ast.unparse(function.args)}){result} | {ast.get_docstring(function) or ''}"
