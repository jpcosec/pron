"""What `clean` leaves of a list field (spec 11 §7): the same items in order, without the
empty ones and without repeats. One rule for the real write and for its dry run.
"""

from __future__ import annotations

import json
from typing import Any


def without_empty_or_repeated(items: list[Any]) -> list[Any]:
    """The items that are not None, "", [] or {}, each first occurrence only (by JSON value)."""
    seen: set[str] = set()
    out: list[Any] = []
    for item in items:
        k = json.dumps(item, sort_keys=True)
        if item in (None, "", [], {}) or k in seen:
            continue
        seen.add(k)
        out.append(item)
    return out
