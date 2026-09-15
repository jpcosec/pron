"""pron's README as a composition (spec 08 step 9, spec 12): the ReadmeDoc declares the
title and the ExplanationDoc files, in order, and `pron docs` renders README.md from it,
so the README is generated and never edited by hand."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from sldb import StructuredNLDoc

from pron.models.explanation import ExplanationDoc


class ReadmeDoc(StructuredNLDoc):
    """The README's declaration: a title and the parts of the README, each the path of an
    ExplanationDoc file rendered as one `## {title}` section with its answer."""

    __family__ = "knowledge"
    __semantics__ = {
        "type": ["knowledge", "readme"],
        "workspace": ["knowledge"],
    }
    __compositions__ = {
        "parts_render": {
            "source_field": "parts",
            "model": "pron.models:ExplanationDoc",
            "template": "## {title}\n\n{answer}",
            "separator": "\n\n",
        }
    }
    __template__ = """# ⸢rev•title⸥

- ⸢rev,list•parts⸥

⸢render•parts_render⸥
""".strip()

    title: str = Field(description="The project name the README opens with, e.g. 'pron'.")
    parts: list[str] = Field(
        description=(
            "Paths of the ExplanationDoc files, in README order. Relative paths resolve "
            "from the process cwd; render with cwd at the world root."
        )
    )

    def render_payload(self) -> dict[str, Any]:
        """The README shows the composed parts, not the paths that declare them: the
        paths list is the authored declaration, dropped from what gets rendered."""
        payload = super().render_payload()
        payload["parts"] = None
        return payload


__all__ = ["ExplanationDoc", "ReadmeDoc"]
