"""The kernel: the action verbs, each one an sldb write (spec 04), plus refresh and undo
(spec 11 §7). Every write is pre-validated, guarded by the document's hash_c, recorded
with its previous value, and followed by a re-evaluation of the conditions of the edges
around the document. Nothing here knows any model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pron.display import render_name, slugify
from pron.store import StoreError
from pron.verbs import Verbs


@dataclass
class Write:
    verb: str
    address: str                     # Model:doc export id
    field_name: str | None = None
    before: Any = None
    after: Any = None
    done: bool = False
    note: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def record(self) -> dict[str, Any]:
        return {"verb": self.verb, "address": self.address, "field": self.field_name, "before": self.before, "after": self.after, "done": self.done, "note": self.note, **self.extra}


class Kernel:
    def __init__(self, verbs: Verbs, projection: dict[str, Any]):
        self.verbs = verbs
        self.world = verbs.world
        self.store = verbs.store
        self.projection = projection
        self.expected_hash: dict[str, str] = {}
        self.warnings: list[str] = []
        self.notes: list[str] = []   # what the last verbs verified, for the trace

    def allowed(self, verb: str) -> bool:
        return verb in (self.projection.get("actions") or [])

    # -- guards ------------------------------------------------------------------------

    def expect(self, export_id: str) -> None:
        model, doc = export_id.split(":", 1)
        self.expected_hash[export_id] = self.store.hash_c(model, doc)

    def _guard(self, export_id: str) -> None:
        model, doc = export_id.split(":", 1)
        expected = self.expected_hash.get(export_id)
        current = self.store.hash_c(model, doc)
        if expected is not None and expected != current:
            raise StoreError(f"{export_id} changed since it was read; not writing")

    def _after_write(self, export_id: str) -> None:
        model, doc = export_id.split(":", 1)
        self.expected_hash[export_id] = self.store.hash_c(model, doc)
        self.warnings += self.verbs.broken_conditions(export_id)

    # -- coercion ---------------------------------------------------------------------------

    def coerce(self, model: str, field_name: str, value: Any) -> Any:
        f = next((x for x in self.store.schema(model) if x["name"] == field_name.split(".")[0]), None)
        if f is None:
            raise StoreError(f"{model} has no field '{field_name}'; it has {', '.join(x['name'] for x in self.store.schema(model))}")
        kind = f["kind"]
        if kind == "integer":
            try:
                return int(value)
            except (TypeError, ValueError):
                raise StoreError(f"{field_name} takes a whole number, not {value!r}")
        if kind == "number":
            return float(value)
        if kind == "boolean":
            return str(value).lower() in ("true", "yes", "on", "1")
        if kind == "enum" and f.get("enum") and value not in f["enum"]:
            raise StoreError(f"{field_name} is one of {', '.join(map(str, f['enum']))}, not {value!r}")
        return value

    def required_missing(self, model: str, payload: dict[str, Any]) -> list[str]:
        return [f["name"] for f in self.store.schema(model) if f["required"] and f["name"] not in payload]

    # -- verbs -------------------------------------------------------------------------------

    def create(self, model: str, payload: dict[str, Any], related: dict[str, dict[str, Any]] | None = None, name: str | None = None) -> Write:
        rule = (self.projection.get("naming") or {}).get(model)
        if name is None:
            if not rule:
                raise StoreError(f"no naming rule for {model}; say the name")
            name = render_name(rule, payload, related or {})
        full = {}
        for f in self.store.schema(model):
            if f["name"] in payload:
                full[f["name"]] = self.coerce(model, f["name"], payload[f["name"]])
        ok, detail = self.store.validate(model, full)
        if not ok:
            raise StoreError(f"{model} payload would not round-trip: {detail}")
        path = self.world.root / f"{model.lower()}s" / f"{name}.md"
        export_id = self.store.create(model, name, full, path)
        w = Write("create", export_id, after=full, done=True, extra={"path": str(path)})
        self._after_write(export_id)
        return w

    def change(self, export_id: str, field_name: str, value: Any) -> Write:
        model, doc = export_id.split(":", 1)
        value = self.coerce(model, field_name, value)
        current = self.store.payload(model, doc)
        before = current.get(field_name.split(".")[0])
        if field_name.split(".")[0] in {f["name"] for f in self.store.schema(model)}:
            legal, why, queries = self.verbs.transition(model, field_name, export_id, before, value)
            self.notes += queries
            if queries or "legal" in why:
                self.notes.append(why)
            if not legal:
                raise StoreError(why)
        self._guard(export_id)
        before = self.store.update_field(model, doc, field_name, value)
        w = Write("change", export_id, field_name, before, value, done=True)
        self._after_write(export_id)
        return w

    def add(self, export_id: str, field_name: str, value: Any) -> Write:
        model, doc = export_id.split(":", 1)
        self._guard(export_id)
        lst = self.store.payload(model, doc).get(field_name)
        if isinstance(lst, list) and value in lst:
            return Write("add", export_id, field_name, lst, lst, done=False, note="already there")
        idx = self.store.append(model, doc, field_name, value)
        w = Write("add", export_id, field_name, None, value, done=True, extra={"index": idx})
        self._after_write(export_id)
        return w

    def remove(self, export_id: str, field_name: str, value: Any = None) -> Write:
        model, doc = export_id.split(":", 1)
        self._guard(export_id)
        if value is not None:
            lst = self.store.payload(model, doc).get(field_name)
            if not isinstance(lst, list) or value not in lst:
                return Write("remove", export_id, field_name, done=False, note="not there")
            before = list(lst); lst.remove(value)
            self.store.update_field(model, doc, field_name, lst)
            w = Write("remove", export_id, field_name, before, lst, done=True)
        else:
            before = self.store.remove_field(model, doc, field_name)
            w = Write("remove", export_id, field_name, before, None, done=True)
        self._after_write(export_id)
        return w

    def clean(self, export_id: str, field_name: str) -> Write:
        model, doc = export_id.split(":", 1)
        self._guard(export_id)
        before = self.store.clean(model, doc, field_name)
        w = Write("clean", export_id, field_name, before, self.store.payload(model, doc).get(field_name), done=True)
        self._after_write(export_id)
        return w

    def forget(self, export_id: str) -> Write:
        model, doc = export_id.split(":", 1)
        path = self.store.doc_path(model, doc)
        payload = self.store.payload(model, doc)
        dependents = self.verbs._edges_sldb("source_id", export_id, None).edges + self.verbs._edges_sldb("target_id", export_id, None).edges
        if dependents:
            raise StoreError(f"{export_id} is an endpoint of {len(dependents)} relation(s); negate them first")
        self._guard(export_id)
        self.store.untrack(doc)
        return Write("forget", export_id, before=payload, done=True, extra={"path": str(path), "hash_c": self.expected_hash.get(export_id, "")})

    def refresh(self) -> dict[str, Any]:
        return self.world.refresh()

    # -- undo ---------------------------------------------------------------------------------

    def undo(self, move: dict[str, Any]) -> list[Write]:
        """Apply the inverses of a recorded move's writes, newest first. Refuses when a document
        changed since, or when an inverse would orphan a later relation."""
        writes = list(reversed(move.get("record", {}).get("writes", [])))
        out: list[Write] = []
        for w in writes:
            if not w.get("done"):
                continue
            verb, address = w["verb"], w["address"]
            model, doc = address.split(":", 1)
            if verb in ("change", "clean") :
                self.expected_hash.pop(address, None)
                before = self.store.update_field(model, doc, w["field"], w["before"])
                out.append(Write("undo", address, w["field"], before, w["before"], done=True))
            elif verb == "add":
                lst = self.store.payload(model, doc).get(w["field"], [])
                if w["after"] in lst:
                    lst.remove(w["after"]); self.store.update_field(model, doc, w["field"], lst)
                out.append(Write("undo", address, w["field"], w["after"], None, done=True))
            elif verb == "remove" and w.get("before") is not None:
                if isinstance(w["before"], list):
                    self.store.update_field(model, doc, w["field"], w["before"])
                else:
                    self.store.update_field(model, doc, w["field"], w["before"], create=True)
                out.append(Write("undo", address, w["field"], None, w["before"], done=True))
            elif verb in ("create", "assert"):
                dependents = self.verbs._edges_sldb("source_id", address, None).edges + self.verbs._edges_sldb("target_id", address, None).edges if verb == "create" else []
                if dependents:
                    raise StoreError(f"undo would orphan {len(dependents)} relation(s) on {address}")
                self.store.untrack(doc)
                out.append(Write("undo", address, None, w.get("after"), None, done=True, note="untracked"))
            elif verb == "forget":
                path = Path(w.get("path", ""))
                if path.exists():
                    self.store.track(path, model, doc)
                    out.append(Write("undo", address, None, None, w.get("before"), done=True, note="tracked again"))
                else:
                    out.append(Write("undo", address, None, None, None, done=False, note="file is gone"))
            self.warnings += self.verbs.broken_conditions(address) if verb != "forget" else []
        return out
