"""A rule of a world, as a document (spec 03, 13): how to prove a goal, or what follows
from an assertion. The rule is data of the world, never code of the engine: a world that
declares no theorems can still be searched with the primitives alone, and a rule lands in
`hash_mundo` like any other document.

    (theorem table-is-free consequent (free ?t)
      (goal (is ?t Table))
      (not (goal (edge assigned_to ?r ?t))))

`pattern` and `body` are forms, written as text: the goal engine reads them, and writing
them as strings keeps sldb's roundtrip on a field it can measure instead of a nested form.
"""

from __future__ import annotations

from pydantic import Field

from sldb import StructuredNLDoc

KINDS = ("consequent", "antecedent")


class TheoremDoc(StructuredNLDoc):
    """One rule of the world: `consequent` proves a goal that matches its pattern;
    `antecedent` fires when something matching its pattern is asserted."""

    __family__ = "knowledge"
    __semantics__ = {
        "type": ["knowledge", "theorem"],
        "workspace": ["knowledge", "theorems"],
    }
    __template__ = """---
name: ⸢rev•name⸥
kind: ⸢rev•kind⸥
pattern: ⸢rev•pattern⸥
body: ⸢rev•body⸥
---

# ⸢render•name⸥

## Motive

⸢rev•motive⸥
""".strip()

    name: str = Field(
        description="Name of the rule, unique in the world; the document is named theorem-<name>."
    )
    kind: str = Field(
        description="consequent (proves a goal matching `pattern`) or antecedent (fires when that pattern is asserted)."
    )
    pattern: str = Field(
        description='The form the rule is about, as text: "(free ?t)", "(transition ?doc ?field ?from ?to)".'
    )
    body: str = Field(
        default="",
        description="The forms that prove it (consequent) or that follow (antecedent), as text, one after the other.",
    )
    motive: str = Field(
        default="",
        description="What the rule means, shown when someone asks; embedded for approximate matching.",
    )
