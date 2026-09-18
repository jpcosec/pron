"""The page of a set an answer carries (spec 14 §2, §3): a set of documents comes cut to a
limit an agent can read — the ten best of a ranked search, fifty of any other set — with its
`total` and, when documents were left out after the page, `truncated: true`. An explicit
`limit` rules, and `offset` walks the pages.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

SEARCH_LIMIT = 10
SET_LIMIT = 50


@dataclass(frozen=True)
class Page:
    """`limit` documents from `offset`; without a limit, the default of the kind of set."""

    limit: int | None = None
    offset: int = 0

    def __post_init__(self) -> None:
        if (self.limit is not None and self.limit < 0) or self.offset < 0:
            raise ValueError("limit and offset are never negative")

    def cut(self, answer: dict[str, Any], default: int = SET_LIMIT) -> dict[str, Any]:
        """The answer with its `documents` paged and counted; any other answer as it is."""
        rows = answer.get("documents")
        if not isinstance(rows, list):
            return answer
        end = self.offset + (default if self.limit is None else self.limit)
        paged = {**answer, "documents": rows[self.offset : end], "total": len(rows)}
        if self.offset:
            paged["offset"] = self.offset
        if end < len(rows):
            paged["truncated"] = True
        return paged
