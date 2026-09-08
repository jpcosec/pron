"""How objects are shown (spec 10): the projection's display templates, `{rel.field}` following an edge."""

from __future__ import annotations

import re
from typing import Any

from pron.graph import doc_id
from pron.resolve import address_to_export_id

FIELD_RE = re.compile(r"\{([A-Za-z_][\w]*)(?:\.([A-Za-z_][\w]*))?\}")


class Display:
    def __init__(self, world, projection: dict[str, Any], verbs):
        self.world = world
        self.templates = projection.get("display") or {}
        self.verbs = verbs

    def name(self, address: str) -> str:
        model, doc = split_address(address)
        d = self.world.store.doc(model, doc)
        if d is None:
            return address
        template = self.templates.get(model)
        if not template:
            for fld in ("title", "name"):
                if fld in d.payload:
                    return str(d.payload[fld])
            return doc
        return self.render(template, model, doc, d.payload)

    def render(self, template: str, model: str, doc: str, payload: dict[str, Any]) -> str:
        def sub(m: re.Match) -> str:
            head, sub_field = m.group(1), m.group(2)
            if sub_field is None:
                return str(payload.get(head, ""))
            targets = self.verbs.targets_of(f"{model}:{doc}", head) if self.verbs else []
            if not targets:
                return ""
            t_model, t_doc = targets[0].split(":", 1)
            td = self.world.store.doc(t_model, t_doc)
            return str(td.payload.get(sub_field, "")) if td else ""
        return FIELD_RE.sub(sub, template).strip()

    def names(self, addresses: list[str]) -> list[str]:
        return [self.name(a) for a in addresses]


def split_address(address: str) -> tuple[str, str]:
    export_id = address_to_export_id(address)
    model, doc = export_id.split(":", 1)
    return model, doc


def slugify(text: str) -> str:
    import unicodedata
    stripped = "".join(c for c in unicodedata.normalize("NFD", str(text)) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", stripped.lower()).strip("-")


def render_name(template: str, payload: dict[str, Any], related: dict[str, dict[str, Any]]) -> str:
    """A naming rule: {field} from the payload, {rel.field} from a related payload, slugified."""
    def sub(m: re.Match) -> str:
        head, sub_field = m.group(1), m.group(2)
        if sub_field is None:
            return slugify(payload.get(head, ""))
        return slugify((related.get(head) or {}).get(sub_field, ""))
    return FIELD_RE.sub(sub, template)
