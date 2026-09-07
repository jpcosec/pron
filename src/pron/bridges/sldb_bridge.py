"""Single door to sldb. Implements atom-bridges-are-the-only-doors-to-sldb-and-kgdb.

Uses the real sldb library layer (load_runtime_documents, resolve_model_ref);
never reimplements search, never shells out to the sldb CLI.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

from sldb.cli.model_utils import resolve_model_ref
from sldb.store.query import load_runtime_documents


class SldbBridge:
    """Read/write access to the local .sldb store and its federated stores."""

    def __init__(self, root: Path, pythonpath: str | None = None) -> None:
        self.root = Path(root).resolve()
        self.store = self.root / ".sldb"
        self.pythonpath = pythonpath or str(self.root)
        self._docs: list | None = None

    def documents(self, include_linked: bool = False) -> list:
        """All tracked RuntimeDocuments (payload already extracted)."""
        if self._docs is None:
            self._docs = load_runtime_documents(
                self.store,
                resolve_model_ref,
                pythonpath=self.pythonpath,
                include_linked=include_linked,
            )
        return self._docs

    def documents_of_model(self, model_name: str) -> list:
        """Tracked documents of one model."""
        return [d for d in self.documents() if d.model_name == model_name]

    def store_hash(self) -> str:
        """Current hash_a of the store (freshness token for session/graph)."""
        index = yaml.safe_load((self.store / "core" / "store_index.yaml").read_text())
        return index.get("hash_a", "")

    def model_names(self) -> list[str]:
        """Names of all registered models."""
        index = yaml.safe_load((self.store / "core" / "store_index.yaml").read_text())
        return [m["name"] for m in index.get("models", [])]

    def filter_where(self, docs: list, expression: str) -> list:
        """Filter documents with sldb's real where engine.

        Supports: has(field) | "needle" in field | field ~ "regex" |
        field = value | field != value (DocumentFilter grammar).
        """
        from sldb.store.query_engine.filter import _where_matches

        return [
            d
            for d in docs
            if _where_matches(d, expression, resolve_model_ref, self.pythonpath)
        ]

    def by_semantic_tag(self, tag: str) -> list:
        """Documents carrying a semantic tag, via the semantic index."""
        return [d for d in self.documents() if tag in (d.semantic_tags or [])]

    def registered_model_ref(self, model_name: str) -> str | None:
        """Map a registered model name to its module:Class ref, via the store index."""
        import yaml

        index = yaml.safe_load((self.store / "core" / "store_index.yaml").read_text())
        for m in index.get("models", []):
            if m.get("name") == model_name:
                return m.get("model_ref")
        return None

    def resolve_model(self, ref: str):
        """Resolve a module:Class model ref at the bridge door."""
        from sldb.cli.model_utils import resolve_model_ref

        return resolve_model_ref(ref, self.pythonpath)

@lru_cache(maxsize=4)
def bridge_for(root: str, pythonpath: str | None = None) -> SldbBridge:
    """Per-invocation cached bridge."""
    return SldbBridge(Path(root), pythonpath)
