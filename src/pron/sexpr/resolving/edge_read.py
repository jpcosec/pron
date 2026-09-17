"""The result of reading edges (spec 03): the edges themselves, whether they came from the
typed graph kgdb built or from the RelationDocs in sldb, and the exact queries it took, so
the trace can say which door answered.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EdgeRead:
    edges: list[dict[str, Any]]  # {source, target, relation, metadata}
    source: str  # "graph" | "sldb"
    queries: list[str] = field(default_factory=list)
