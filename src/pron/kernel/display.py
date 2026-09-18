"""How objects are shown (spec 10): the projection's display templates, `{rel.field}` following an edge.

A template is parts between separators (`, ` or `; `). A missing value leaves its gap empty
(spec 09a), and a part all of whose gaps are empty is left out with its separator: a
reservation without a table is "2026-09-12 13:00, 2 people, pending", not
"…, table , pending". A template with nothing left falls back to the untemplated name.

`render_name` is the same substitution used the other way round: a projection's naming rule
turned into the document name a `create` writes.
"""

from __future__ import annotations

import re
from typing import Any

from pron.kernel.ids import export_id, split_id
from pron.world.doc_id import DocId

FIELD_RE = re.compile(r"\{([A-Za-z_][\w]*)(?:\.([A-Za-z_][\w]*))?\}")
SEPARATOR_RE = re.compile(r"(\s*[,;]\s*)")


class Display:
    def __init__(self, world, projection: dict[str, Any], verbs):
        self.world = world
        self.templates = projection.get("display") or {}
        self.verbs = verbs

    def name(self, address: str) -> str:
        store, model, doc = split_address(address)
        d = self.world.store.doc(DocId.of(model, doc, store))
        if d is None:
            return address
        template = self.templates.get(model)
        rendered = (
            self.render(template, model, doc, d.payload, export_id(address))
            if template
            else ""
        )
        return rendered or untemplated_name(doc, d.payload)

    def render(
        self,
        template: str,
        model: str,
        doc: str,
        payload: dict[str, Any],
        eid: str | None = None,
    ) -> str:
        def value(m: re.Match) -> str:
            head, sub_field = m.group(1), m.group(2)
            if sub_field is None:
                return str(payload.get(head, ""))
            targets = (
                self.verbs.targets_of(
                    export_id(f"{model}:{doc}") if not eid else eid, head
                )
                if self.verbs
                else []
            )
            if not targets:
                return ""
            td = self.world.store.doc(DocId.parse(targets[0]))
            return str(td.payload.get(sub_field, "")) if td else ""

        pieces = SEPARATOR_RE.split(template)  # part, separator, part, …
        kept: list[str] = []
        for i in range(0, len(pieces), 2):
            if text := render_part(pieces[i], value):
                kept += [pieces[i - 1] if kept else "", text]
        return "".join(kept).strip()

    def names(self, addresses: list[str]) -> list[str]:
        return [self.name(a) for a in addresses]


def render_part(part: str, value) -> str:
    """One part of a display template; empty if it has gaps and all of them are empty. A part
    with some gaps empty closes the spaces they leave."""
    values = {m.group(0): value(m) for m in FIELD_RE.finditer(part)}
    if values and not any(values.values()):
        return ""
    text = FIELD_RE.sub(lambda m: values[m.group(0)], part)
    return " ".join(text.split()) if "" in values.values() else text


def untemplated_name(doc: str, payload: dict[str, Any]) -> str:
    """Spec 10: without a template, `title` if the document has one (or `name`), else its name."""
    for fld in ("title", "name"):
        if fld in payload:
            return str(payload[fld])
    return doc


def split_address(address: str) -> tuple[str | None, str, str]:
    """(store, model, doc) of an address or an export id."""
    return split_id(export_id(address))


def slugify(text: str) -> str:
    import unicodedata

    stripped = "".join(
        c
        for c in unicodedata.normalize("NFD", str(text))
        if unicodedata.category(c) != "Mn"
    )
    return re.sub(r"[^a-z0-9]+", "-", stripped.lower()).strip("-")


def render_name(
    template: str, payload: dict[str, Any], related: dict[str, dict[str, Any]]
) -> str:
    """A naming rule: {field} from the payload, {rel.field} from a related payload, slugified."""

    def sub(m: re.Match) -> str:
        head, sub_field = m.group(1), m.group(2)
        if sub_field is None:
            return slugify(payload.get(head, ""))
        return slugify((related.get(head) or {}).get(sub_field, ""))

    return FIELD_RE.sub(sub, template)
