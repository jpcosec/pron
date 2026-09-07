"""Doc contracts for write-produced knowledge docs, defined at the bridge door.

The bridge is the only door to sldb, so the StructuredNLDoc contracts that the
write ops produce live here. Implements
atom-write-operations-record-provenance-of-the-command-that-produced-them:
every write-produced doc carries the full evaluated command in its provenance
field, plus the timestamp of the write.
"""

from typing import Annotated

from pydantic import Field

from sldb import StructuredNLDoc

KnowledgeTag = Annotated[
    str,
    Field(
        pattern=r"^[a-z][a-z0-9_]*:[a-z][a-z0-9_.-]*$",
        description="Namespaced semantic tag in the form namespace:value.",
    ),
]


class FactDoc(StructuredNLDoc):
    """A fact asserted as true by (assert ...).

    Implements atom-write-operations-record-provenance-of-the-command-that-produced-them:
    provenance holds the exact s-expression that produced the fact.
    """

    __semantics__ = {
        "type": ["knowledge", "fact"],
        "workspace": ["knowledge", "facts"],
    }
    __template__ = """---
id: ⸢rev•id⸥
fact: ⸢rev•fact⸥
tags: ⸢rev•tags⸥
provenance: ⸢optrev•provenance⸥
provenance_at: ⸢optrev•provenance_at⸥
---

# ⸢render•id⸥

## Fact

⸢render•fact⸥
""".strip()

    id: str = Field(
        description="Stable id, conventionally 'fact-<slug>-<timestamp>'."
    )
    fact: str = Field(
        description="The asserted statement, stored verbatim as a true fact."
    )
    tags: list[KnowledgeTag] = Field(
        default_factory=list,
        description="Namespaced semantic tags for retrieval and grouping.",
    )
    provenance: str | None = Field(
        default=None,
        description="The full evaluated s-expression command that produced this fact.",
    )
    provenance_at: str | None = Field(
        default=None,
        description="UTC ISO-8601 timestamp of the write that produced this fact.",
    )


class PropositionDoc(StructuredNLDoc):
    """A proposition or document registered by (ingest ...).

    Implements atom-write-operations-record-provenance-of-the-command-that-produced-them:
    provenance holds the exact s-expression that produced the registration.
    """

    __semantics__ = {
        "type": ["knowledge", "proposition"],
        "workspace": ["knowledge", "propositions"],
    }
    __template__ = """---
id: ⸢rev•id⸥
title: ⸢rev•title⸥
proposition: ⸢rev•proposition⸥
tags: ⸢rev•tags⸥
provenance: ⸢optrev•provenance⸥
provenance_at: ⸢optrev•provenance_at⸥
---

# ⸢render•title⸥

## Proposition

⸢render•proposition⸥
""".strip()

    id: str = Field(
        description="Stable id, conventionally 'proposition-<timestamp>'."
    )
    title: str = Field(
        description="Short human title of the ingested proposition or document."
    )
    proposition: str = Field(
        description="The registered content: a proposition or document text, stored verbatim."
    )
    tags: list[KnowledgeTag] = Field(
        default_factory=list,
        description="Namespaced semantic tags for retrieval and grouping.",
    )
    provenance: str | None = Field(
        default=None,
        description="The full evaluated s-expression command that produced this registration.",
    )
    provenance_at: str | None = Field(
        default=None,
        description="UTC ISO-8601 timestamp of the write that produced this registration.",
    )
