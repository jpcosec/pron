"""The result of reading edges (spec 03): the edges themselves and the exact queries it took,
so the trace can say what was asked.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EdgeRead:
    edges: list[dict[str, Any]]  # {source, target, relation, metadata}
    queries: list[str] = field(default_factory=list)
