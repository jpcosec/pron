"""The kernel: the action verbs, each one an sldb write (spec 04), plus refresh and undo
(spec 11 §7). Every write is pre-validated, guarded by the document's hash_c, recorded
with its previous value, and followed by a re-evaluation of the conditions of the edges
around the document. Nothing here knows any model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import json

from sldb.cli.dict_utils import deep_delete, deep_get, deep_set

from pron.display import render_name
from pron.ids import join_id, model_of, split_id, store_of
from pron.store import StoreError
from pron.verbs import Verbs


@dataclass
class Write:
    verb: str
    address: str  # Model:doc export id
    field_name: str | None = None
    before: Any = None
    after: Any = None
    done: bool = False
    note: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def record(self) -> dict[str, Any]:
        return {
            "verb": self.verb,
            "address": self.address,
            "field": self.field_name,
            "before": self.before,
            "after": self.after,
            "done": self.done,
            "note": self.note,
            **self.extra,
        }


class Kernel:
    def __init__(self, verbs: Verbs, projection: dict[str, Any]):
        self.verbs = verbs
        self.world = verbs.world
        self.store = verbs.store
        self.projection = projection
        self.write_store = (
            verbs.write_store
        )  # where create puts a document: the projection's first store
        self.stores = list(verbs.stores)
        self.expected_hash: dict[str, str] = {}
        self.warnings: list[str] = []
        self.notes: list[str] = []  # what the last verbs verified, for the trace

    def allowed(self, verb: str) -> bool:
        return verb in (self.projection.get("actions") or [])

    # -- guards ------------------------------------------------------------------------

    def expect(self, export_id: str) -> None:
        self.expected_hash[export_id] = self.store.hash_of(export_id)

    def _guard(self, export_id: str) -> None:
        expected = self.expected_hash.get(export_id)
        current = self.store.hash_of(export_id)
        if expected is not None and expected != current:
            raise StoreError(f"{export_id} changed since it was read; not writing")

    def _after_write(self, export_id: str, w: Write) -> None:
        """Replace the expected hash by the one sldb left, record it in the write for undo, and
        re-evaluate the conditions around the document."""
        self.expected_hash[export_id] = w.extra["hash_c"] = self.store.hash_of(
            export_id
        )
        self.warnings += self.verbs.broken_conditions(export_id)

    # -- pre-validation (spec 11 §7) --------------------------------------------------------

    def dry_run(
        self,
        verb: str,
        export_id: str,
        field_name: str | None,
        value: Any,
        overlay: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """What a write would leave, without writing: coercion, the transition over the payloads
        this move has already planned, and sldb's roundtrip of the new payload. Leaves the new
        payload in `overlay` so the next write of the move sees it."""
        model = model_of(export_id)
        p = json.loads(
            json.dumps(overlay.get(export_id) or self.store.payload_of(export_id))
        )
        head = field_name.split(".")[0] if field_name else None
        if verb == "change":
            if field_name is None:
                raise StoreError("change requires a field")
            value = self.coerce(model, field_name, value)
            legal, why, queries = self.verbs.transition(
                model, field_name, export_id, p.get(head), value, overlay=overlay
            )
            self.notes += queries
            if queries or "legal" in why:
                self.notes.append(why)
            if not legal:
                raise StoreError(why)
            deep_set(p, field_name, value, create=True)
        elif verb == "add":
            lst = deep_get(p, field_name) if head in p else None
            if not isinstance(lst, list):
                raise StoreError(f"{field_name} is not a list field")
            if value not in lst:
                lst.append(value)
        elif verb == "remove":
            if value is not None:
                lst = p.get(head)
                if isinstance(lst, list) and value in lst:
                    lst.remove(value)
            elif head in p:
                deep_delete(p, field_name)
        elif verb == "clean":
            lst = p.get(head)
            if isinstance(lst, list):
                seen, out = set(), []
                for item in lst:
                    k = json.dumps(item, sort_keys=True)
                    if item in (None, "", [], {}) or k in seen:
                        continue
                    seen.add(k)
                    out.append(item)
                p[head] = out
        elif verb == "forget":
            return p
        ok, detail = self.store.validate(model, p, store_of(export_id))
        if not ok:
            raise StoreError(f"{model} payload would not round-trip: {detail}")
        overlay[export_id] = p
        return p

    def dry_create(
        self, model: str, payload: dict[str, Any], overlay: dict[str, dict[str, Any]]
    ) -> dict[str, Any]:
        """The payload a create would leave, coerced and round-tripped, registered in the overlay
        as `Model:$created` so later steps of the move can be checked against it."""
        missing = self.required_missing(model, payload)
        if missing:
            raise StoreError(f"{model} needs {', '.join(missing)}")
        full = {
            f["name"]: self.coerce(model, f["name"], payload[f["name"]])
            for f in self.schema(model)
            if f["name"] in payload
        }
        ok, detail = self.store.validate(model, full, self.write_store)
        if not ok:
            raise StoreError(f"{model} payload would not round-trip: {detail}")
        overlay[join_id(self.write_store, model, "$created")] = full
        return full

    # -- coercion ---------------------------------------------------------------------------

    def schema(self, model: str) -> list[dict[str, Any]]:
        return self.world.schema(model, self.stores)

    def coerce(self, model: str, field_name: str, value: Any) -> Any:
        f = next(
            (x for x in self.schema(model) if x["name"] == field_name.split(".")[0]),
            None,
        )
        if f is None:
            raise StoreError(
                f"{model} has no field '{field_name}'; it has {', '.join(x['name'] for x in self.schema(model))}"
            )
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
            raise StoreError(
                f"{field_name} is one of {', '.join(map(str, f['enum']))}, not {value!r}"
            )
        return value

    def required_missing(self, model: str, payload: dict[str, Any]) -> list[str]:
        return [
            f["name"]
            for f in self.schema(model)
            if f["required"] and f["name"] not in payload
        ]

    # -- verbs -------------------------------------------------------------------------------

    def create(
        self,
        model: str,
        payload: dict[str, Any],
        related: dict[str, dict[str, Any]] | None = None,
        name: str | None = None,
    ) -> Write:
        rule = (self.projection.get("naming") or {}).get(model)
        if name is None:
            if not rule:
                raise StoreError(f"no naming rule for {model}; say the name")
            name = render_name(rule, payload, related or {})
        full = {}
        for f in self.schema(model):
            if f["name"] in payload:
                full[f["name"]] = self.coerce(model, f["name"], payload[f["name"]])
        ok, detail = self.store.validate(model, full, self.write_store)
        if not ok:
            raise StoreError(f"{model} payload would not round-trip: {detail}")
        path = self.store.root_of(self.write_store) / f"{model.lower()}s" / f"{name}.md"
        export_id = self.store.create(model, name, full, path, self.write_store)
        w = Write("create", export_id, after=full, done=True, extra={"path": str(path)})
        self._after_write(export_id, w)
        return w

    def change(self, export_id: str, field_name: str, value: Any) -> Write:
        model = model_of(export_id)
        value = self.coerce(model, field_name, value)
        current = self.store.payload_of(export_id)
        before = current.get(field_name.split(".")[0])
        if field_name.split(".")[0] in {f["name"] for f in self.schema(model)}:
            legal, why, queries = self.verbs.transition(
                model, field_name, export_id, before, value
            )
            self.notes += queries
            if queries or "legal" in why:
                self.notes.append(why)
            if not legal:
                raise StoreError(why)
        self._guard(export_id)
        before = self.store.update_field_of(export_id, field_name, value)
        w = Write("change", export_id, field_name, before, value, done=True)
        self._after_write(export_id, w)
        return w

    def add(self, export_id: str, field_name: str, value: Any) -> Write:
        self._guard(export_id)
        lst = self.store.payload_of(export_id).get(field_name)
        if isinstance(lst, list) and value in lst:
            return Write(
                "add", export_id, field_name, lst, lst, done=False, note="already there"
            )
        idx = self.store.append_of(export_id, field_name, value)
        w = Write(
            "add", export_id, field_name, None, value, done=True, extra={"index": idx}
        )
        self._after_write(export_id, w)
        return w

    def remove(self, export_id: str, field_name: str, value: Any = None) -> Write:
        self._guard(export_id)
        if value is not None:
            lst = self.store.payload_of(export_id).get(field_name)
            if not isinstance(lst, list) or value not in lst:
                return Write(
                    "remove", export_id, field_name, done=False, note="not there"
                )
            before = list(lst)
            lst.remove(value)
            self.store.update_field_of(export_id, field_name, lst)
            w = Write("remove", export_id, field_name, before, lst, done=True)
        else:
            before = self.store.remove_field_of(export_id, field_name)
            w = Write("remove", export_id, field_name, before, None, done=True)
        self._after_write(export_id, w)
        return w

    def clean(self, export_id: str, field_name: str) -> Write:
        self._guard(export_id)
        before = self.store.clean_of(export_id, field_name)
        w = Write(
            "clean",
            export_id,
            field_name,
            before,
            self.store.payload_of(export_id).get(field_name),
            done=True,
        )
        self._after_write(export_id, w)
        return w

    def forget(self, export_id: str) -> Write:
        store, model, doc = split_id(export_id)
        path = self.store.doc_path(model, doc, store)
        payload = self.store.payload_of(export_id)
        dependents = (
            self.verbs._edges_sldb("source_id", export_id, None).edges
            + self.verbs._edges_sldb("target_id", export_id, None).edges
        )
        if dependents:
            raise StoreError(
                f"{export_id} is an endpoint of {len(dependents)} relation(s); negate them first"
            )
        self._guard(export_id)
        self.store.untrack_of(export_id)
        return Write(
            "forget",
            export_id,
            before=payload,
            done=True,
            extra={"path": str(path), "hash_c": self.expected_hash.get(export_id, "")},
        )

    def refresh(self) -> dict[str, Any]:
        return self.world.refresh()

    # -- undo ---------------------------------------------------------------------------------

    def undo(self, move: dict[str, Any]) -> list[Write]:
        """Apply the inverses of a recorded move's writes, newest first (spec 11 §7). Before
        touching anything: a write whose document changed since the move (a different hash_c
        from the one the move left) is skipped and named; an inverse that would orphan a
        later relation rejects the whole undo."""
        writes = [
            w
            for w in reversed(move.get("record", {}).get("writes", []))
            if w.get("done")
        ]
        out: list[Write] = []
        todo: list[dict[str, Any]] = []
        for w in writes:
            verb, address = w["verb"], w["address"]
            if verb == "forget":
                todo.append(w)
                continue
            left = w.get("hash_c")
            current = self.store.hash_of(address)
            if left and current and left != current:
                out.append(
                    Write(
                        "undo",
                        address,
                        w.get("field"),
                        None,
                        None,
                        done=False,
                        note=f"{address} changed after that move; not touched",
                    )
                )
                continue
            if verb == "create":
                dependents = (
                    self.verbs._edges_sldb("source_id", address, None).edges
                    + self.verbs._edges_sldb("target_id", address, None).edges
                )
                if dependents:
                    raise StoreError(
                        f"undo would orphan {len(dependents)} relation(s) on {address}: "
                        + ", ".join(
                            e["metadata"].get("relation_doc", e["relation"])
                            for e in dependents
                        )
                    )
            todo.append(w)
        for w in todo:
            verb, address = w["verb"], w["address"]
            store, model, doc = split_id(address)
            self.expected_hash.pop(address, None)
            if verb in ("change", "clean"):
                before = self.store.update_field_of(address, w["field"], w["before"])
                out.append(
                    Write("undo", address, w["field"], before, w["before"], done=True)
                )
            elif verb == "add":
                lst = self.store.payload_of(address).get(w["field"], [])
                if w["after"] in lst:
                    lst.remove(w["after"])
                    self.store.update_field_of(address, w["field"], lst)
                out.append(
                    Write("undo", address, w["field"], w["after"], None, done=True)
                )
            elif verb == "remove" and w.get("before") is not None:
                if isinstance(w["before"], list):
                    self.store.update_field_of(address, w["field"], w["before"])
                else:
                    self.store.update_field_of(
                        address, w["field"], w["before"], create=True
                    )
                out.append(
                    Write("undo", address, w["field"], None, w["before"], done=True)
                )
            elif verb in ("create", "assert"):
                self.store.untrack_of(address)
                out.append(
                    Write(
                        "undo",
                        address,
                        None,
                        w.get("after"),
                        None,
                        done=True,
                        note="untracked",
                    )
                )
            elif verb == "forget":
                path = Path(w.get("path", ""))
                if path.exists():
                    self.store.track(path, model, doc, store)
                    out.append(
                        Write(
                            "undo",
                            address,
                            None,
                            None,
                            w.get("before"),
                            done=True,
                            note="tracked again",
                        )
                    )
                else:
                    out.append(
                        Write(
                            "undo",
                            address,
                            None,
                            None,
                            None,
                            done=False,
                            note="file is gone",
                        )
                    )
            if verb != "forget":
                self.warnings += self.verbs.broken_conditions(address)
        return out
