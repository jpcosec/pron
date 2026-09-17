"""A predicate over a document that does not exist yet (spec 11 §7): sldb's own evaluator,
with any document of the model lending its runtime shape and the pending payload as its
content, so a condition on what a move is about to create is checked the way sldb would.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from pron.world.store_error import StoreError


def pending_matches(
    store, model: str, where: str, payload: dict[str, Any], in_store: str | None = None
) -> bool:
    """sldb's evaluator over a document that does not exist yet: any document of the model
    lends its runtime shape, the payload is the pending one."""
    from sldb.store.query_engine.filter import DocumentFilter
    from sldb.store.query_engine.where_parse import WherePredicateError
    from sldb.api import resolve_model_ref

    sample = next(iter(store.docs_of(model, in_store or "local")), None) or next(
        iter(store.docs_of(model, "*")), None
    )
    if sample is None:
        return (
            True  # nothing to compare the shape against; the write itself will validate
        )
    try:
        return DocumentFilter.where_matches(
            replace(sample, name="$created", payload=payload),
            where,
            resolve_model_ref,
            store.pythonpath,
        )
    except WherePredicateError as e:
        raise StoreError(str(e)) from e
