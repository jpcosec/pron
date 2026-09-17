"""Whether a tracked document drifted from its source (spec 08 step 9): it is missing, or one
of the fields its source renders reads differently in the store.
"""

from __future__ import annotations

from typing import Any


def drifted(existing: Any, canonical: dict[str, Any]) -> bool:
    """True unless the document exists and holds every canonical field as its source says."""
    return existing is None or {k: existing.payload.get(k) for k in canonical} != canonical
