"""How objects are shown (spec 10): the projection's display templates, `{rel.field}` following an edge."""

from __future__ import annotations

import re
from typing import Any

from pron.ids import export_id, split_id

FIELD_RE = re.compile(r"\{([A-Za-z_][\w]*)(?:\.([A-Za-z_][\w]*))?\}")


class Display:
    def __init__(self, world, projection: dict[str, Any], verbs):
        self.world = world
        self.templates = projection.get("display") or {}
        self.verbs = verbs

    def name(self, address: str) -> str:
        store, model, doc = split_address(address)
        d = self.world.store.doc(model, doc, store)
        if d is None:
            return address
        template = self.templates.get(model)
        if not template:
            for fld in ("title", "name"):
                if fld in d.payload:
                    return str(d.payload[fld])
            return doc
        return self.render(template, model, doc, d.payload, export_id(address))

    def render(
        self,
        template: str,
        model: str,
        doc: str,
        payload: dict[str, Any],
        eid: str | None = None,
    ) -> str:
        def sub(m: re.Match) -> str:
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
            td = self.world.store.doc_of(targets[0])
            return str(td.payload.get(sub_field, "")) if td else ""

        return FIELD_RE.sub(sub, template).strip()

    def names(self, addresses: list[str]) -> list[str]:
        return [self.name(a) for a in addresses]


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
