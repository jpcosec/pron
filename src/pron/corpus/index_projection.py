"""What a consumer declares about its corpus (spec 12 §5b), re-exported from sldb: which
documents it admits and how it reads the representative text of one.
"""

from __future__ import annotations

from sldb.api.corpus.index_projection import IndexProjection, fields_text, summary_text

__all__ = ["IndexProjection", "fields_text", "summary_text"]
