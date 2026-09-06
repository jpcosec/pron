"""Noun resolver: (model, selector) -> Resolved | Ambiguous | Missing.

Implements atom-symbol-resolution-is-stateful-and-treats-ambiguity-as-dialogue:
exact id, then exact title, then prefix; fuzzy only populates `nearest`.
"""
from __future__ import annotations

from difflib import get_close_matches

from knowledge.bridges.sldb_bridge import SldbBridge
from knowledge.core.results import Ambiguous, Missing, Resolved


def resolve_noun(
    bridge: SldbBridge, model_name: str, selector: str, motive: str,
) -> Resolved | Ambiguous | Missing:
    """Resolve a selector against the tracked documents of a model."""
    docs = bridge.documents_of_model(model_name)
    if not docs:
        return Missing(motive=motive, nearest=[])

    exact = [d for d in docs if d.name == selector]
    if len(exact) == 1:
        return _resolved(exact[0])

    by_title = [
        d for d in docs
        if str(d.payload.get("title", "")).lower() == selector.lower()
    ]
    if len(by_title) == 1:
        return _resolved(by_title[0])

    prefix = [d for d in docs if d.name.startswith(selector)]
    if len(prefix) == 1:
        return _resolved(prefix[0])
    if len(prefix) > 1:
        names = sorted(d.name for d in prefix)
        return Ambiguous(
            question=f"Ambiguo: ¿{' o '.join(repr(n) for n in names[:5])}?",
            candidates=names,
        )

    nearest = get_close_matches(selector, [d.name for d in docs], n=3, cutoff=0.5)
    return Missing(motive=motive, nearest=nearest)


def _resolved(doc) -> Resolved:
    return Resolved(
        name=doc.name, model=doc.model_name,
        path=str(doc.path), payload=dict(doc.payload),
    )
