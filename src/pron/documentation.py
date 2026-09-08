"""Describe public surfaces from source contracts; atom-pron-cli-and-modules-are-documented-from-source."""

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
    commands = _command_specs()
    surfaces = [
        _module_spec(path, root, atoms)
        for path in sorted((root / "src/pron").rglob("*.py"))
        if not path.name.startswith("__")
    ]
    return (*commands, *surfaces)


_GUIDES: dict[str, dict[str, str]] = {
    "anchors": {
        "synopsis": "List the live grammar: anchors bound to models, expressions and operations.",
        "how_it_works": "Reads AnchorDoc documents tracked in the store through AnchorRegistry and renders each symbol's kind, ref and motive. With a symbol argument, resolves and renders that one anchor.",
        "arguments": '[symbol] | optional | Filter to a single anchor symbol.\n--kb <root> | optional | KB root; defaults to the current working directory.\n--format json|text | optional | Output projection; defaults to json.',
        "usage": "pron anchors\npron anchors atom --format text",
    },
    "eval": {
        "synopsis": "Evaluate an s-expression directly against the Meaning layer.",
        "how_it_works": "Parses the expression with pron.core.sexpr, resolves nouns and anchors through AnchorRegistry, and evaluates it with Evaluator against SLDB and KGDB. Ambiguous resolutions are persisted as a pending clarification in .pron/session.json.",
        "arguments": "<s-expr> | required | The s-expression to evaluate, e.g. '(check (doc atom \"x\") :project title)'.\n--kb <root> | optional | KB root; defaults to the current working directory.\n--format json|text | optional | Output projection; defaults to json.",
        "usage": 'pron eval \'(check (doc atom "atom-x") :project title)\'',
    },
    "anchor add": {
        "synopsis": "Declare a new grammar symbol: writes an AnchorDoc and tracks it.",
        "how_it_works": "Validates symbol, kind, ref and motive, writes the AnchorDoc through the sldb bridge, tracks it and refreshes the store so the symbol resolves on the next call.",
        "arguments": "<symbol> | required | The grammar symbol being declared.\n--kind model|expr|operation | required | The anchor's kind.\n--ref <typed-ref> | required | The referent, e.g. model:AtomDoc or 'expr:(related (doc atom _))'.\n--motive <text> | required | The semantic motive for the symbol.\n--kb <root> | optional | KB root; defaults to the current working directory.\n--format json|text | optional | Output projection; defaults to json.",
        "usage": 'pron anchor add tagged --kind expr --ref "expr:(rel tagged _)" --motive "..."',
    },
    "model add": {
        "synopsis": "Register a StructuredNLDoc model contract in the local store.",
        "how_it_works": "Delegates to `sldb models add` against the local .sldb store, given a module:Class reference, so the evaluator and write ops can resolve and validate documents of that model.",
        "arguments": "<module:Class> | required | The model reference to register, e.g. pron.bridges.write_models:FactDoc.\n--kb <root> | optional | KB root; defaults to the current working directory.",
        "usage": "pron model add pron.bridges.write_models:FactDoc",
    },
    "project": {
        "synopsis": "Refresh SLDB indexes and rebuild the KGDB graph.",
        "how_it_works": "Runs `sldb stores update` to reindex every tracked document (semantic index, sections), then semantic-exports the store and ingests it into the KGDB snapshot at .sldb/runtime/knowledge.nx.json.",
        "arguments": "--kb <root> | optional | KB root; defaults to the current working directory.",
        "usage": "pron project",
    },
    "docs": {
        "synopsis": "Derive CLI command docs and module surface docs from the source tree.",
        "how_it_works": "Describes every base CLI command from a hand-authored guide (kept next to the command's implementation) and every public module under src/pron from its AST, registers CliCommandDoc/SurfaceDoc if needed, writes and tracks the documents, and refreshes the store. --check instead verifies there is no drift, that every generated document is tracked, that every authored document is tracked, and that tags/provenance/roundtrip/store integrity all hold, without writing anything.",
        "arguments": "--check | optional | Verify instead of regenerating; exits non-zero on drift.\n--kb <root> | optional | KB root; defaults to the current working directory.",
        "usage": "pron docs\npron docs --check",
    },
}


def _command_specs() -> list[DocumentSpec]:
    specs = []
    for name, guide in _GUIDES.items():
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
                    "synopsis": guide["synopsis"],
                    "purpose": guide["synopsis"],
                    "how_it_works": guide["how_it_works"],
                    "arguments": guide["arguments"],
                    "usage": guide["usage"],
                    "tags": [
                        "system:pron",
                        "domain:system_architecture",
                        "kind:software",
                        "impl:here",
                    ],
                    "provenance": "src/pron/cli/main.py:main",
                },
            )
        )
    return specs


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
