"""One question about pron, answered as a small typed document so an agent reads the
world by address (spec 08, 12): `(doc "ExplanationDoc:what-is-pron")` answers
"what is pron?" without opening the README. The README itself is a composition of these."""

from __future__ import annotations

from pydantic import Field

from sldb import StructuredNLDoc


class ExplanationDoc(StructuredNLDoc):
    """One question this world answers about itself: the question, the answer in
    markdown, and the addresses the answer rests on (spec chapters, commands, surfaces).
    Small on purpose, so a question is answered by address instead of by search."""

    __family__ = "knowledge"
    __semantics__ = {
        "type": ["knowledge", "explanation"],
        "workspace": ["knowledge", "explanations"],
    }
    __template__ = """# ⸢rev•title⸥

## Question

⸢rev•question⸥

## Answer

⸢rev•answer⸥

## Sources

- ⸢rev,list•sources⸥
""".strip()

    title: str = Field(description="The section title this answer holds in the README.")
    question: str = Field(description="The one question this document answers.")
    answer: str = Field(description="The answer, in markdown.")
    sources: list[str] = Field(
        default_factory=list,
        description=(
            "Addresses this answer rests on, e.g. 'SpecDoc:spec-12' or "
            "'CliCommandDoc:cmd-pron-serve'. An empty list is allowed."
        ),
    )
