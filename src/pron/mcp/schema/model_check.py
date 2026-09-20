"""Whether a generated model module works before it is registered (spec 14 §4, nivel 3).

The substrate owns the check now (ADR 2026-09-20): this re-exports sldb's `ModelCheck`
instead of keeping its own copy.
"""

from sldb.api.model_create.model_check import (
    EXAMPLES,
    ModelCheck,
    example,
    example_payload,
)

__all__ = ["EXAMPLES", "ModelCheck", "example", "example_payload"]
