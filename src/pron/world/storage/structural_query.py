"""Querying a store by address (spec 02): `find` by one `--where` predicate, `list`, `get`
and `glob` over `[store:]st.{Model[+]}.doc` addresses, and sldb's own predicate evaluator
over one document or over a payload not saved yet (spec 11 §7). Always sldb's grammar,
never pron's; an unparseable predicate is an error, never an empty set.
"""

from __future__ import annotations

import builtins
from typing import Any

from sldb.api import resolve_model_ref
from sldb.store.query import (
    find_structural,
    get_structural,
    glob_structural,
    list_structural,
)
from sldb.store.query_engine.filter import DocumentFilter
from sldb.store.query_engine.where_parse import WherePredicateError

from pron.world.doc_id import LOCAL, DocId
from pron.world.storage.document_reader import DocumentReader
from pron.world.store_error import StoreError


class StructuralQuery(DocumentReader):
    """sldb's structural queries and `--where` evaluator over this world's stores."""

    def find(self, scope: str, where: str) -> builtins.list[str]:
        """Addresses `[store:]st.{Model[+]}.doc` matching one predicate."""
        try:
            return find_structural(
                self.sp, scope, where, resolve_model_ref, self.pythonpath
            )
        except WherePredicateError as e:
            raise StoreError(
                str(e)
            ) from e  # an unparseable predicate is an error, never an empty set

    def list(self, address: str) -> builtins.list[str]:
        return list_structural(self.sp, address, resolve_model_ref, self.pythonpath)

    def get(self, address: str) -> Any:
        return get_structural(self.sp, address, resolve_model_ref, self.pythonpath)

    def glob(self, pattern: str) -> builtins.list[str]:
        return glob_structural(self.sp, pattern, resolve_model_ref, self.pythonpath)

    def matches_at(
        self, doc_id: DocId, where: str, payload: dict | None = None
    ) -> bool:
        """sldb's own `--where` evaluator over one document; with `payload`, over a payload that
        is not saved yet (the pre-validation of a move, spec 11 §7). Still sldb's grammar, never
        pron's."""
        from dataclasses import replace

        d = self.doc_at(doc_id)
        if d is None:
            raise StoreError(f"no {doc_id.model} named '{doc_id.name}'")
        if payload is not None:
            d = replace(d, payload=payload)
        try:
            return DocumentFilter.where_matches(
                d, where, resolve_model_ref, self.pythonpath
            )
        except WherePredicateError as e:
            raise StoreError(str(e)) from e

    def matches(
        self,
        model: str,
        name: str,
        where: str,
        payload: dict | None = None,
        store: str | None = LOCAL,
    ) -> bool:
        """`matches_at`, the document named by model, name and store."""
        return self.matches_at(DocId.of(model, name, store), where, payload)

    def matches_of(
        self, export_id: str, where: str, payload: dict | None = None
    ) -> bool:
        """`matches_at`, the document named by its export id."""
        return self.matches_at(DocId.parse_plain(export_id), where, payload)
