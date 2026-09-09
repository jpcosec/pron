"""An alias: a word that names something the world already has."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from sldb import StructuredNLDoc

REF_FORMS = ("model", "field", "predicate", "relation", "action", "doc", "compose")


class AnchorDoc(StructuredNLDoc):
    """A word of the lexicon and what it names. `ref` takes one of seven forms:
    model:M · field:M.f · predicate:M:<where> · relation:R · action:<verb> M.f=v ·
    doc:M:name · compose (with `steps`). An alias adds a form of speech, never a
    capability: everything a ref names can already be reached by address or command.
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
        description="What the word names: model:M | field:M.f | predicate:M:<where> | relation:R | action:<verb> M.f=v | doc:M:name | compose."
    )
    steps: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Only for ref compose: ordered steps {do: create|assert|change, model|relation, fields|source|target} with slots $literals, $created, $referent:M, $object:M.",
    )
    motive: str = Field(
        description="What the word means, shown when someone asks; embedded for approximate matching."
    )
