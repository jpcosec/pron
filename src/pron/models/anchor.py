"""An alias: a word that names something the world already has (spec 01, 05)."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from sldb import StructuredNLDoc

REF_FORMS = ("model", "field", "where", "relation", "doc", "change", "move")


class AnchorDoc(StructuredNLDoc):
    """A word of the lexicon and what it names, as a form (spec 05, 13): (model M) ·
    (field M f) · (where M "<predicate>") · (relation R) · (doc "M:name") ·
    (change (it "it" M) f "v") · (move (create M) (assert R (created) (it "her" M2)) …).
    The older string refs (model:M, predicate:M:<where>, action:change M.f=v, compose
    with `steps`) are still read and turned into forms. An alias adds a form of speech,
    never a capability: everything a ref names can already be reached by address or command.
    """

    __family__ = "knowledge"
    __semantics__ = {
        "type": ["knowledge", "anchor"],
        "workspace": ["knowledge", "anchors"],
    }
    __template__ = """---
symbol: ⸢rev•symbol⸥
forms: ⸢rev•forms⸥
ref: ⸢rev•ref⸥
steps: ⸢rev•steps⸥
---

# ⸢render•symbol⸥

## Motive

⸢rev•motive⸥
""".strip()

    symbol: str = Field(
        description="Canonical word of the alias; the document is named anchor-<symbol>."
    )
    forms: list[str] = Field(
        default_factory=list,
        description="Every surface form the parser recognizes, listed (no morphology): 'reservation, reservations'. May use N for a number slot and X for a free slot.",
    )
    ref: str = Field(
        description='What the word names, as a form: (model M) | (field M f) | (where M "<predicate>") | (relation R) | (doc "M:name") | (change (it "it" M) f "v") | (move (create M) (assert R (created) (it "her" M2)) ...). The older string refs are read too.'
    )
    steps: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Only for the older string ref 'compose': ordered steps {do, model|relation, fields|source|target}. A ref written as (move …) needs none.",
    )
    motive: str = Field(
        description="What the word means, shown when someone asks; embedded for approximate matching."
    )
