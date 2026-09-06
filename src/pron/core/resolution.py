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
        return _ambiguous(prefix)

    # semantic tag: a namespaced selector matches docs tagged with it
    if ":" in selector:
        tagged = [d for d in docs if selector in (d.semantic_tags or [])]
        if len(tagged) == 1:
            return _resolved(tagged[0])
        if len(tagged) > 1:
            return _ambiguous(tagged)

    # substring over name and title (sldb-style physical match)
    loose = [
        d for d in docs
        if selector.lower() in d.name.lower()
        or selector.lower() in str(d.payload.get("title", "")).lower()
    ]
    if len(loose) == 1:
        return _resolved(loose[0])
    if len(loose) > 1:
        return _ambiguous(loose)

    nearest = get_close_matches(selector, [d.name for d in docs], n=3, cutoff=0.5)
    return Missing(motive=motive, nearest=nearest)


def _ambiguous(docs: list) -> Ambiguous:
    names = sorted(d.name for d in docs)
    return Ambiguous(
        question=f"Ambiguo: ¿{' o '.join(repr(n) for n in names[:5])}?",
        candidates=names,
    )


def _resolved(doc) -> Resolved:
    return Resolved(
        name=doc.name, model=doc.model_name,
        path=str(doc.path), payload=dict(doc.payload),
    )
