"""A chapter of pron's specification, tracked as a document so it is addressable by
section and can be the target of `implements` edges from the code that carries it out."""

from __future__ import annotations

from pydantic import Field

from sldb import StructuredNLDoc


class SpecDoc(StructuredNLDoc):
    """One chapter of source/spec: its title and its whole body. sldb indexes the sections
    (breadcrumbs, about terms, line ranges), so a chapter is reachable by section address;
    pron's modules implement chapters, and that edge is derived from the spec references
    in their docstrings.
    """

    __family__ = "knowledge"
    __semantics__ = {
        "type": ["knowledge", "spec"],
        "workspace": ["source", "spec"],
    }
    __template__ = """# ⸢rev•title⸥

⸢rev•body⸥
""".strip()

    title: str = Field(description="Chapter title as its H1, e.g. '02 · Sustantivos'.")
    body: str = Field(
        description="The chapter's whole markdown body after the H1: sections, tables, code blocks."
    )
