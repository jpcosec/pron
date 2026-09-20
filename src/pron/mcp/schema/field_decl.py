"""One field of a model declared in JSON (spec 14 §4, nivel 3).

The substrate owns the declaration now (ADR 2026-09-20, sldb-absorbs-kgdb): this module
re-exports sldb's `FieldDecl` instead of keeping its own copy.
"""

from sldb.api.model_create.field_decl import EMPTY, TYPES, FieldDecl

__all__ = ["EMPTY", "FieldDecl", "TYPES"]
