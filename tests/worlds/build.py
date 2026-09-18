"""How a test world is built from its declaration under data/: the models package written
where the world's pythonpath finds it, a store with those models, and its documents created
in order. What a world declares lives in data/; this is only the mechanics."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml
from sldb.cli import main as sldb_main

from pron.world.doc_id import DocId
from pron.world.world import World, init_world

DATA = Path(__file__).parent / "data"

# (model, name, payload, path relative to the world root)
Doc = tuple[str, str, dict[str, Any], Path]


def load_data(name: str) -> dict[str, Any]:
    return yaml.safe_load((DATA / name).read_text(encoding="utf-8"))


def _run(argv: list[str]) -> None:
    assert sldb_main(argv) == 0, argv


def _write_package(pythonpath: Path, package: str, models_source: str) -> None:
    sys.modules.pop(package, None)
    sys.modules.pop(f"{package}.models", None)
    pkg = pythonpath / package
    pkg.mkdir(parents=True, exist_ok=True)
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    source = (DATA / models_source).read_text(encoding="utf-8")
    (pkg / "models.py").write_text(source, encoding="utf-8")


def start_world(
    pythonpath: Path, root: Path, package: str, models_source: str, models: list[str]
) -> World:
    """The models package under pythonpath, a store at root with those models, opened as a world."""
    _write_package(pythonpath, package, models_source)
    root.mkdir(parents=True, exist_ok=True)
    _run(["stores", "init", "--path", str(root)])
    common = ["--store", str(root / ".sldb"), "--pythonpath", str(pythonpath)]
    for model in models:
        _run(["models", "add", f"{package}.models:{model}", *common])
    init_world(root, str(pythonpath))
    return World(root, str(pythonpath))


def create_docs(world: World, root: Path, docs: list[Doc]) -> None:
    for model, name, payload, path in docs:
        world.store.create(DocId.of(model, name), payload, root / path)


def declared_docs(data: dict[str, Any]) -> list[Doc]:
    """The documents a world's data spells out whole."""
    return [
        (d["model"], d["name"], d["payload"], Path(d["path"]))
        for d in data["documents"]
    ]


def relation_type_docs(data: dict[str, Any]) -> list[Doc]:
    return [
        (
            "RelationTypeDoc",
            f"rt-{rt['name']}",
            {"title": rt["name"], "direction": "directed", **rt},
            Path("relations") / "types" / f"{rt['name']}.md",
        )
        for rt in data["relation_types"]
    ]


def relation_doc(
    relation: str, source: str, target: str, title: str, condition: str = ""
) -> Doc:
    name = f"{relation}--{source}--{target}"
    payload = {
        "title": title,
        "source_id": source,
        "target_id": target,
        "relation_type": relation,
        "condition": condition,
        "notes": "",
    }
    return ("RelationDoc", name, payload, Path("relations") / f"{name}.md")


def projection_doc(data: dict[str, Any]) -> Doc:
    path = Path("knowledge") / "projections" / "all.md"
    return ("ProjectionDoc", "projection-all", data["projection"], path)


def anchor_docs(data: dict[str, Any]) -> list[Doc]:
    docs: list[Doc] = []
    for anchor in data["anchors"]:
        slug = anchor["symbol"].replace(" ", "-").lower()
        path = Path("knowledge") / "anchors" / f"{slug}.md"
        docs.append(("AnchorDoc", f"anchor-{slug}", anchor, path))
    return docs
