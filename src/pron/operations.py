from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import yaml

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)
ANSWER_RE = re.compile(r"## Answer\n\n(.*?)(?:\n## |\Z)", re.S)


@dataclass
class Atom:
    path: Path
    frontmatter: dict[str, Any]
    body: str

    @property
    def id(self) -> str:
        return str(self.frontmatter.get("id", ""))

    @property
    def title(self) -> str:
        return str(self.frontmatter.get("title", ""))

    @property
    def tags(self) -> list[str]:
        tags = self.frontmatter.get("tags") or []
        return [str(tag) for tag in tags]

    def to_dict(self, root: Path) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "tags": self.tags,
            "path": self.path.relative_to(root).as_posix(),
        }

class KnowledgeOperations:
    """
    Capa de operaciones para Knowledge.
    Diseñada para ser extensible: aquí se inyectarán las llamadas a SLDB y KGDB
    sin acoplarse a lógicas específicas de agentes (como kb_agent).
    """
    def __init__(self, store_path: Path):
        self._store_path = store_path

    def _atoms_dir(self) -> Path:
        preferred = self._store_path / ".knowledge" / "atoms"
        legacy = self._store_path / "desk" / "atoms"
        return preferred if preferred.exists() or not legacy.exists() else legacy

    def _iter_atoms(self) -> list[Atom]:
        out = []
        for path in sorted(self._atoms_dir().rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            match = FRONTMATTER_RE.match(text)
            if not match:
                continue
            frontmatter_text, body = match.groups()
            frontmatter = yaml.safe_load(frontmatter_text) or {}
            out.append(Atom(path=path, frontmatter=frontmatter, body=body))
        return out

    def list_atoms(self, args) -> int:
        atoms = [a.to_dict(self._store_path) for a in self._iter_atoms()]
        if args.format == "json":
            print(json.dumps(atoms, indent=2, ensure_ascii=False))
            return 0
        for atom in atoms:
            print(f"{atom['id']} | {atom['title']}")
        return 0

    def show_atom(self, args) -> int:
        atoms = self._iter_atoms()
        selector = args.selector
        exact = [a for a in atoms if selector in {a.id, a.path.name, a.path.stem}]
        atom = exact[0] if exact else None

        if not atom:
            fuzzy = [a for a in atoms if selector in a.id or selector in a.path.stem]
            if fuzzy:
                atom = fuzzy[0]

        if not atom:
            print(f"Atom not found: {selector}")
            return 1
            
        data = atom.to_dict(self._store_path)
        if args.format == "json":
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return 0

        print(f"ID: {atom.id}")
        print(f"Title: {atom.title}")
        print(f"Path: {data['path']}")
        print("Tags:")
        for tag in atom.tags:
            print(f"  - {tag}")
        return 0

    def explore(self, args) -> int:
        # Placeholder para la integración real con KGDBReader y sldb en el futuro
        print(f"Explorando el knowledge graph con query: {args.query}")
        print("(La integración con sldb/kgdb debe añadirse aquí como capa abstracta)")
        return 0