"""The approximate-matching port, re-exported from sldb (spec 11 §2): an application
injects an Embedder; without one pron falls back to difflib.
"""

from __future__ import annotations

from sldb.api.matching.embedder_protocol import Embedder

__all__ = ["Embedder"]
