"""A knowledge atom of pron's own world."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field

from sldb import StructuredNLDoc

AtomTag = Annotated[
    str,
    Field(pattern=r"^[a-z][a-z0-9_]*:[a-z][a-z0-9_.-]*$", description="Namespaced semantic tag, namespace:value."),
]


class Atom(StructuredNLDoc):
    """One stable claim of knowledge about pron or about another system: the single
    question it answers, its answer, its tags and where it comes from.

    Same template as the v1 AtomDoc except that `five_wh_one_plus` is named
    `question`, so v1 atoms migrate by renaming one frontmatter key.
    """

    __family__ = "knowledge"
    __semantics__ = {
        "type": ["knowledge", "atom"],
        "workspace": ["knowledge", "atoms"],
    }
    __template__ = """---
id: ⸢rev•id⸥
title: ⸢rev•title⸥
question: ⸢rev•question⸥
tags: ⸢rev•tags⸥
provenance: ⸢rev•provenance⸥
---

# ⸢render•title⸥

## Answer

⸢rev•answer⸥
""".strip()

    id: str = Field(description="Stable, unique atom identifier, conventionally 'atom-<slug>'.")
    title: str = Field(description="Short, descriptive title for the atomic knowledge unit.")
    question: Literal["what", "why", "how", "how_not", "when", "where", "for_whom"] = Field(
        description="The single 5W1H+ question this atom answers."
    )
    answer: str = Field(description="The curated answer to the question, written as one stable knowledge unit.")
    tags: list[AtomTag] = Field(
        default_factory=list,
        description="Namespaced semantic tags for retrieval and grouping, namespace:value; relations are edges, not tags.",
    )
    provenance: str = Field(default="", description="Path, URL or move id of the authoritative source of this atom.")
