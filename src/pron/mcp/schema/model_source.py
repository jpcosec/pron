"""The Python module of a model declared in JSON (spec 14 §4, nivel 3).

The substrate owns the generated module now (ADR 2026-09-20): this re-exports sldb's
`ModelSource` instead of keeping its own copy.
"""

from sldb.api.model_create.model_source import HEADER, ModelSource

__all__ = ["HEADER", "ModelSource"]
