"""The only door to sldb: read by address (spec 02), write by address (spec 04), never open Markdown.

Every method is a call into sldb's library. sldb caches the runtime documents by the
store's hash chain, so reading them here costs nothing and is never stale. A world's store
may link other stores (spec 01 §Un mundo en varios stores); every method that names a
document takes the store it lives in, `None` or "local" for the local one, and the
`*_of(export_id)` forms take the id `store:Model:doc` that carries it.
"""

from __future__ import annotations

import json
import builtins
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from pydantic import BaseModel

from sldb.cli.commands.doc import DocCLI
from sldb.cli.commands.fields_save import save_payload
from sldb.cli.commands.model import ModelCLI
from sldb.cli.dict_utils import deep_delete, deep_get, deep_set
from sldb.cli.model_utils import registered_model, resolve_model_ref
from sldb.cli.serve.schema import field_descriptor
from sldb.cli.store_context import get_store_context
from sldb.core.exceptions import SLDBModelError
from sldb.runtime.validation import (
    render_model_markdown,
    validate_model_data_roundtrip,
    validate_model_input_roundtrip,
)
from sldb.store.io import load_documents_index, load_models_index, load_store_index
from sldb.store.layout import project_root as _project_root
from sldb.store.ops import track_document
from sldb.store.query import (
    find_structural,
    get_structural,
    glob_structural,
    list_structural,
    load_runtime_documents,
)
from sldb.store.query_engine.filter import DocumentFilter

from pron.ids import LOCAL, is_local, join_id, split_id


class StoreError(RuntimeError):
    """sldb refused or could not do what was asked."""


class Store:
    """Read/write access to one world's .sldb store, and the stores it links, through sldb's library."""

    def __init__(self, root: str | Path, pythonpath: str | None = None) -> None:
        self.root = Path(root).resolve()
        self.sp, self.project_root = get_store_context(str(self.root / ".sldb"))
        self.pythonpath = pythonpath or str(self.root)

    # -- stores ----------------------------------------------------------------

    def linked(self) -> dict[str, Path]:
        """name -> .sldb path of every store linked into this one."""
        out = {}
        for s in self.store_index().stores:
            p = Path(s.path)
            out[s.name] = (p if p.is_absolute() else self.project_root / p).resolve()
        return out

    def names(self) -> list[str]:
        return [LOCAL, *self.linked()]

    def sp_of(self, store: str | None) -> Path:
        if is_local(store):
            return self.sp
        assert store is not None
        try:
            return self.linked()[store]
        except KeyError:
            raise StoreError(f"no store linked as '{store}'") from None

    def root_of(self, store: str | None) -> Path:
        return (
            self.project_root if is_local(store) else _project_root(self.sp_of(store))
        )

    def link(self, name: str, other_root: str | Path) -> bool:
        """Link another world's store under a name (sldb stores add). False when already linked."""
        from sldb.cli.commands.store_add import _link_store

        if name in self.linked():
            return False
        _link_store(
            self.sp, self.project_root, Path(other_root).resolve() / ".sldb", name
        )
        return True

    # -- reading ---------------------------------------------------------------

    def docs(self) -> list:
        """The runtime documents of the local store and every linked one, from sldb's cache."""
        return load_runtime_documents(
            self.sp,
            resolve_model_ref,
            self.pythonpath,
            include_linked=bool(self.store_index().stores),
        )

    def invalidate(self) -> None:
        """Kept for callers; sldb's cache invalidates itself by the hash chain."""

    def docs_of(self, model: str, store: str | None = LOCAL) -> list:
        """Documents of a model in one store, or in every store with store='*'."""
        return [
            d
            for d in self.docs()
            if d.model_name == model
            and (store == "*" or d.store_name == (store or LOCAL))
        ]

    def doc(self, model: str, name: str, store: str | None = LOCAL):
        for d in self.docs():
            if (
                d.model_name == model
                and d.name == name
                and d.store_name == (store or LOCAL)
            ):
                return d
        return None

    def doc_of(self, export_id: str):
        store, model, name = split_id(export_id)
        return self.doc(model, name, store)

    def find(self, scope: str, where: str) -> list[str]:
        """Addresses `[store:]st.{Model[+]}.doc` matching one predicate."""
        return find_structural(
            self.sp, scope, where, resolve_model_ref, self.pythonpath
        )

    def list(self, address: str) -> list[str]:
        return list_structural(self.sp, address, resolve_model_ref, self.pythonpath)

    def get(self, address: str) -> Any:
        return get_structural(self.sp, address, resolve_model_ref, self.pythonpath)

    def glob(self, pattern: str) -> builtins.list[str]:
        return glob_structural(self.sp, pattern, resolve_model_ref, self.pythonpath)

    # -- schema ----------------------------------------------------------------

    def store_index(self, store: str | None = LOCAL):
        return load_store_index(self.sp_of(store))

    def model_names(self, store: str | None = LOCAL) -> builtins.list[str]:
        return [m.name for m in self.store_index(store).models]

    def models_index(self, name: str, store: str | None = LOCAL):
        entry = next(
            (m for m in self.store_index(store).models if m.name == name), None
        )
        if entry is None:
            raise StoreError(
                f"model '{name}' is not registered"
                + ("" if is_local(store) else f" in store '{store}'")
            )
        return load_models_index(self.root_of(store) / entry.models_index)

    def model_type(self, name: str, store: str | None = LOCAL) -> type[BaseModel]:
        try:
            return registered_model(self.sp_of(store), name, self.pythonpath)[0]
        except Exception:  # noqa: BLE001 - a linked store's models import from where that store lives
            if is_local(store):
                raise
            return registered_model(self.sp_of(store), name, str(self.root_of(store)))[
                0
            ]

    def schema(
        self, name: str, store: str | None = LOCAL
    ) -> builtins.list[dict[str, Any]]:
        """Fields of a model: name, kind, required, enum, annotation, description."""
        model_type = self.model_type(name, store)
        out = []
        for fname, finfo in model_type.model_fields.items():
            d = field_descriptor(fname, finfo)
            d["annotation"] = getattr(
                finfo.annotation, "__name__", repr(finfo.annotation)
            )
            d["description"] = finfo.description or ""
            out.append(d)
        return out

    def hash_c(self, model: str, name: str, store: str | None = LOCAL) -> str:
        m_idx = self.models_index(model, store)
        for d in load_documents_index(
            self.root_of(store) / m_idx.documents_index
        ).documents:
            if d.name == name:
                return d.hash_c
        return ""

    def hash_of(self, export_id: str) -> str:
        store, model, name = split_id(export_id)
        return self.hash_c(model, name, store)

    def matches(
        self,
        model: str,
        name: str,
        where: str,
        payload: dict | None = None,
        store: str | None = LOCAL,
    ) -> bool:
        """sldb's own `--where` evaluator over one document; with `payload`, over a payload that
        is not saved yet (the pre-validation of a move, spec 11 §7). Still sldb's grammar, never
        pron's."""
        from dataclasses import replace

        d = self.doc(model, name, store)
        if d is None:
            raise StoreError(f"no {model} named '{name}'")
        if payload is not None:
            d = replace(d, payload=payload)
        return DocumentFilter.where_matches(
            d, where, resolve_model_ref, self.pythonpath
        )

    def matches_of(
        self, export_id: str, where: str, payload: dict | None = None
    ) -> bool:
        store, model, name = split_id(export_id)
        return self.matches(model, name, where, payload, store)

    def doc_path(self, model: str, name: str, store: str | None = LOCAL) -> Path | None:
        m_idx = self.models_index(model, store)
        root = self.root_of(store)
        for d in load_documents_index(root / m_idx.documents_index).documents:
            if d.name == name:
                return root / d.path
        return None

    # -- writing ---------------------------------------------------------------

    def register_model(self, ref: str) -> bool:
        try:
            ModelCLI().add(
                SimpleNamespace(
                    model=ref,
                    store=str(self.sp),
                    pythonpath=self.pythonpath,
                    canonical=False,
                )
            )
        except SLDBModelError:
            return False
        return True

    def validate(
        self, model: str, payload: dict, store: str | None = LOCAL
    ) -> tuple[bool, str]:
        ok, details = validate_model_data_roundtrip(
            self.model_type(model, store), payload
        )
        return ok, "" if ok else json.dumps(
            details.get("extracted_payload"), default=str
        )[:200]

    def create(
        self,
        model: str,
        name: str,
        payload: dict,
        path: Path,
        store: str | None = LOCAL,
    ) -> str:
        """Render, validate and track one new document in a store. Returns the export id."""
        sp, root = self.sp_of(store), self.root_of(store)
        model_type, entry, idx = registered_model(
            sp,
            model,
            self.pythonpath if is_local(store) else self._pythonpath_for(store, model),
        )
        if self.doc(model, name, store) is not None:
            raise StoreError(
                f"a {model} named '{name}' already exists"
                + ("" if is_local(store) else f" in store '{store}'")
            )
        rendered = render_model_markdown(model_type, payload)
        ok, details = validate_model_input_roundtrip(model_type, rendered)
        if not ok:
            raise StoreError(
                f"{model} '{name}' would not round-trip: {json.dumps(details.get('extracted_payload'), default=str)[:200]}"
            )
        path = self._under(root, path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered + "\n", encoding="utf-8")
        track_document(
            sp,
            root,
            idx,
            model_type,
            entry,
            path,
            name,
            resolve_model_ref,
            self.pythonpath,
        )
        return join_id(store, model, name)

    def _pythonpath_for(self, store: str | None, model: str) -> str:
        try:
            registered_model(self.sp_of(store), model, self.pythonpath)
            return self.pythonpath
        except Exception:  # noqa: BLE001
            return str(self.root_of(store))

    @staticmethod
    def _under(root: Path, path: Path) -> Path:
        """A relative document path is relative to the store's root, never to the process cwd:
        sldb records paths relative to the root, so a cwd-relative file would be tracked as missing."""
        path = Path(path)
        return path if path.is_absolute() else root / path

    def _save(
        self, model: str, name: str, payload: dict, store: str | None = LOCAL
    ) -> None:
        d = self.doc(model, name, store)
        if d is None:
            raise StoreError(f"no {model} named '{name}'")
        save_payload(d, payload, str(self.sp_of(store)), self.pythonpath)

    def payload(self, model: str, name: str, store: str | None = LOCAL) -> dict:
        d = self.doc(model, name, store)
        if d is None:
            raise StoreError(
                f"no {model} named '{name}'"
                + ("" if is_local(store) else f" in store '{store}'")
            )
        return json.loads(json.dumps(d.payload))

    def payload_of(self, export_id: str) -> dict:
        store, model, name = split_id(export_id)
        return self.payload(model, name, store)

    def update_field(
        self,
        model: str,
        name: str,
        field_path: str,
        value: Any,
        create: bool = False,
        store: str | None = LOCAL,
    ) -> Any:
        """Set one field (dotted path into subfields and list items). Returns the previous value."""
        p = self.payload(model, name, store)
        try:
            before = deep_get(p, field_path)
        except (KeyError, IndexError):
            before = None
        deep_set(p, field_path, value, create=create)
        self._save(model, name, p, store)
        return before

    def update_field_of(
        self, export_id: str, field_path: str, value: Any, create: bool = False
    ) -> Any:
        store, model, name = split_id(export_id)
        return self.update_field(model, name, field_path, value, create, store)

    def remove_field(
        self, model: str, name: str, field_path: str, store: str | None = LOCAL
    ) -> Any:
        p = self.payload(model, name, store)
        before = deep_get(p, field_path)
        deep_delete(p, field_path)
        self._save(model, name, p, store)
        return before

    def remove_field_of(self, export_id: str, field_path: str) -> Any:
        store, model, name = split_id(export_id)
        return self.remove_field(model, name, field_path, store)

    def append(
        self,
        model: str,
        name: str,
        field_path: str,
        value: Any,
        store: str | None = LOCAL,
    ) -> int:
        """Append to a list field. Returns the index of the new item."""
        p = self.payload(model, name, store)
        lst = deep_get(p, field_path)
        if not isinstance(lst, list):
            raise StoreError(f"{field_path} is not a list field")
        lst.append(value)
        self._save(model, name, p, store)
        return len(lst) - 1

    def append_of(self, export_id: str, field_path: str, value: Any) -> int:
        store, model, name = split_id(export_id)
        return self.append(model, name, field_path, value, store)

    def clean(
        self, model: str, name: str, field_path: str, store: str | None = LOCAL
    ) -> builtins.list:
        p = self.payload(model, name, store)
        lst = deep_get(p, field_path)
        before = list(lst)
        seen, out = set(), []
        for item in lst:
            k = json.dumps(item, sort_keys=True)
            if item in (None, "", [], {}) or k in seen:
                continue
            seen.add(k)
            out.append(item)
        deep_set(p, field_path, out)
        self._save(model, name, p, store)
        return before

    def clean_of(self, export_id: str, field_path: str) -> builtins.list:
        store, model, name = split_id(export_id)
        return self.clean(model, name, field_path, store)

    def untrack(self, name: str, store: str | None = LOCAL) -> None:
        DocCLI().untrack(
            SimpleNamespace(
                doc=name, store=str(self.sp_of(store)), pythonpath=self.pythonpath
            )
        )

    def untrack_of(self, export_id: str) -> None:
        store, _, name = split_id(export_id)
        self.untrack(name, store)

    def track(
        self, path: Path, model: str, name: str, store: str | None = LOCAL
    ) -> None:
        sp, root = self.sp_of(store), self.root_of(store)
        model_type, entry, idx = registered_model(
            sp,
            model,
            self.pythonpath if is_local(store) else self._pythonpath_for(store, model),
        )
        track_document(
            sp,
            root,
            idx,
            model_type,
            entry,
            self._under(root, path),
            name,
            resolve_model_ref,
            self.pythonpath,
        )
