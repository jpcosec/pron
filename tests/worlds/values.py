"""A minimal world for PLAN 11 (value suggestions and the glossary), built from scratch.

Mirrors legos' clinic world's Fact model (topic/statement) so the same real texts the plan
measured there ("evento adverso", "evento_adversso") exercise the same paths here, plus an
Atom model with a `system` field to exercise PLAN 11 P3 (values already used in `system`/
`tags` enter the lexicon).
"""

from __future__ import annotations

import sys
from pathlib import Path

from sldb.cli import main as sldb_main

from pron.world import World, init_world

MODELS = '''from pydantic import Field
from sldb import StructuredNLDoc


class Fact(StructuredNLDoc):
    """A piece of business knowledge an agent can be asked about."""
    __family__ = "values"
    __semantics__ = {"type": ["values", "fact"]}
    __template__ = """---
topic: ⸢rev•topic⸥
---

# ⸢render•topic⸥

⸢rev•statement⸥
""".strip()

    topic: str = Field(description="What this fact is about, e.g. evento_adverso.")
    statement: str = Field(description="The fact itself, in plain language.")


class Atom(StructuredNLDoc):
    """A small piece of knowledge that belongs to a system."""
    __family__ = "values"
    __semantics__ = {"type": ["values", "atom"]}
    __template__ = """---
system: ⸢rev•system⸥
label: ⸢rev•label⸥
---

# ⸢render•label⸥
""".strip()

    system: str = Field(description="Which system this atom belongs to.")
    label: str = Field(description="A short name for this atom.")
'''

FACTS = [
    (
        "evento-adverso",
        "evento_adverso",
        "An adverse event report is always routed to human review.",
    ),
    (
        "medinfo",
        "medinfo",
        "A MedInfo question is answered from the product sheet when one exists.",
    ),
    (
        "seguimiento",
        "seguimiento",
        "A follow-up call happens a week after an adverse event report.",
    ),
]

ATOMS = [
    ("atom-lexicon", "pron", "lexicon"),
    ("atom-resolve", "pron", "resolve"),
    ("atom-bridge", "legos", "bridge"),
]

PROJECTION = {
    "name": "all",
    "stores": ["local"],
    "models": ["Fact", "Atom"],
    "relations": [],
    "actions": ["create", "refresh"],
    "aliases": ["all"],
    "naming": {"Fact": "fact-{topic}", "Atom": "atom-{label}"},
    "display": {"Fact": "{topic}: {statement}", "Atom": "{system}: {label}"},
    "matching": {"neighbors": 3, "threshold": 0.55},
    "description": "A minimal world for PLAN 11's value-suggestion and glossary tests.",
}

ALIASES = [
    ("fact", ["fact", "facts"], "model:Fact", "a piece of business knowledge", []),
    (
        "about",
        ["about", "on", "regarding"],
        "field:Fact.topic",
        "which topic a fact concerns",
        [],
    ),
    ("atom", ["atom", "atoms"], "model:Atom", "a small piece of knowledge", []),
]


def _run(argv: list[str]) -> None:
    assert sldb_main(argv) == 0, argv


def build_values(root: Path, refresh: bool = True) -> World:
    """Build the values world directly at root/ and return it opened."""
    sys.modules.pop("values_models", None)
    sys.modules.pop("values_models.models", None)
    pythonpath = root.parent
    pkg = pythonpath / "values_models"
    pkg.mkdir(parents=True, exist_ok=True)
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "models.py").write_text(MODELS, encoding="utf-8")
    root.mkdir(parents=True, exist_ok=True)
    _run(["stores", "init", "--path", str(root)])
    common = ["--store", str(root / ".sldb"), "--pythonpath", str(pythonpath)]
    _run(["models", "add", "values_models.models:Fact", *common])
    _run(["models", "add", "values_models.models:Atom", *common])
    init_world(root, str(pythonpath))
    world = World(root, str(pythonpath))
    s = world.store
    for slug, topic, statement in FACTS:
        s.create(
            "Fact",
            f"fact-{slug}",
            {"topic": topic, "statement": statement},
            root / "facts" / f"{slug}.md",
        )
    for slug, system, label in ATOMS:
        s.create(
            "Atom",
            slug,
            {"system": system, "label": label},
            root / "atoms" / f"{slug}.md",
        )
    s.create(
        "ProjectionDoc",
        "projection-all",
        PROJECTION,
        root / "knowledge" / "projections" / "all.md",
    )
    for symbol, forms, ref, motive, steps in ALIASES:
        s.create(
            "AnchorDoc",
            f"anchor-{symbol}",
            {
                "symbol": symbol,
                "forms": forms,
                "ref": ref,
                "steps": steps,
                "motive": motive,
            },
            root / "knowledge" / "anchors" / f"{symbol}.md",
        )
    if refresh:
        world.refresh()
    return world
