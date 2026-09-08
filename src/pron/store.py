"""The only door to sldb: read by address, write by address, never open Markdown.

Every method is a call into sldb's library. The address engine loads every document
of the store before selecting (an sldb cost, not pron's), so the runtime documents
are cached here and invalidated on every write.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from sldb.cli.commands.doc import DocCLI
from sldb.cli.commands.fields_save import save_payload
from sldb.cli.commands.model import ModelCLI
from sldb.cli.dict_utils import deep_delete, deep_get, deep_set
from sldb.cli.model_utils import registered_model, resolve_model_ref
from sldb.cli.serve.schema import field_descriptor
from sldb.cli.store_context import get_store_context
from sldb.core.exceptions import SLDBModelError
from sldb.runtime.validation import render_model_markdown, validate_model_data_roundtrip, validate_model_input_roundtrip
from sldb.store.io import load_documents_index, load_models_index, load_store_index
from sldb.store.ops import track_document
from sldb.store.query import find_structural, get_structural, glob_structural, list_structural, load_runtime_documents


class StoreError(RuntimeError):
    """sldb refused or could not do what was asked."""


class Store:
    """Read/write access to one world's .sldb store through sldb's library."""

    def __init__(self, root: str | Path, pythonpath: str | None = None) -> None:
        self.root = Path(root).resolve()
        self.sp, self.project_root = get_store_context(str(self.root / ".sldb"))
        self.pythonpath = pythonpath or str(self.root)
        self._docs: list | None = None

    # -- reading ---------------------------------------------------------------

    def docs(self) -> list:
        if self._docs is None:
            self._docs = load_runtime_documents(self.sp, resolve_model_ref, self.pythonpath)
        return self._docs

    def invalidate(self) -> None:
        self._docs = None

    def docs_of(self, model: str) -> list:
        return [d for d in self.docs() if d.model_name == model]

    def doc(self, model: str, name: str):
        for d in self.docs():
            if d.model_name == model and d.name == name:
                return d
        return None

    def find(self, scope: str, where: str) -> list[str]:
        """Addresses `st.{Model[+]}.doc` matching one predicate."""
        return find_structural(self.sp, scope, where, resolve_model_ref, self.pythonpath)

    def list(self, address: str) -> list[str]:
        return list_structural(self.sp, address, resolve_model_ref, self.pythonpath)

    def get(self, address: str) -> Any:
        return get_structural(self.sp, address, resolve_model_ref, self.pythonpath)

    def glob(self, pattern: str) -> list[str]:
        return glob_structural(self.sp, pattern, resolve_model_ref, self.pythonpath)

    # -- schema ----------------------------------------------------------------

    def store_index(self):
        return load_store_index(self.sp)

    def model_names(self) -> list[str]:
        return [m.name for m in self.store_index().models]

    def models_index(self, name: str):
        entry = next((m for m in self.store_index().models if m.name == name), None)
        if entry is None:
            raise StoreError(f"model '{name}' is not registered")
        return load_models_index(self.project_root / entry.models_index)

    def model_type(self, name: str) -> type:
        return registered_model(self.sp, name, self.pythonpath)[0]

    def schema(self, name: str) -> list[dict[str, Any]]:
        """Fields of a model: name, kind, required, enum, annotation, description."""
        model_type = self.model_type(name)
        out = []
        for fname, finfo in model_type.model_fields.items():
            d = field_descriptor(fname, finfo)
            d["annotation"] = getattr(finfo.annotation, "__name__", repr(finfo.annotation))
            d["description"] = finfo.description or ""
            out.append(d)
        return out

    def hash_c(self, model: str, name: str) -> str:
        m_idx = self.models_index(model)
        for d in load_documents_index(self.project_root / m_idx.documents_index).documents:
            if d.name == name:
                return d.hash_c
        return ""

    def doc_path(self, model: str, name: str) -> Path | None:
        m_idx = self.models_index(model)
        for d in load_documents_index(self.project_root / m_idx.documents_index).documents:
            if d.name == name:
                return self.project_root / d.path
        return None

    # -- writing ---------------------------------------------------------------

    def register_model(self, ref: str) -> bool:
        try:
            ModelCLI().add(SimpleNamespace(model=ref, store=str(self.sp), pythonpath=self.pythonpath, canonical=False))
        except SLDBModelError:
            return False
        self.invalidate()
        return True

    def validate(self, model: str, payload: dict) -> tuple[bool, str]:
        ok, details = validate_model_data_roundtrip(self.model_type(model), payload)
        return ok, "" if ok else json.dumps(details.get("extracted_payload"), default=str)[:200]

    def create(self, model: str, name: str, payload: dict, path: Path) -> str:
        """Render, validate and track one new document. Returns the export id Model:name."""
        model_type, entry, idx = registered_model(self.sp, model, self.pythonpath)
        if self.doc(model, name) is not None:
            raise StoreError(f"a {model} named '{name}' already exists")
        rendered = render_model_markdown(model_type, payload)
        ok, details = validate_model_input_roundtrip(model_type, rendered)
        if not ok:
            raise StoreError(f"{model} '{name}' would not round-trip: {json.dumps(details.get('extracted_payload'), default=str)[:200]}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered + "\n", encoding="utf-8")
        track_document(self.sp, self.project_root, idx, model_type, entry, path, name, resolve_model_ref, self.pythonpath)
        self.invalidate()
        return f"{model}:{name}"

    def _save(self, model: str, name: str, payload: dict) -> None:
        d = self.doc(model, name)
        if d is None:
            raise StoreError(f"no {model} named '{name}'")
        save_payload(d, payload, str(self.sp), self.pythonpath)
        self.invalidate()

    def payload(self, model: str, name: str) -> dict:
        d = self.doc(model, name)
        if d is None:
            raise StoreError(f"no {model} named '{name}'")
        return json.loads(json.dumps(d.payload))

    def update_field(self, model: str, name: str, field_path: str, value: Any, create: bool = False) -> Any:
        """Set one field (dotted path into subfields and list items). Returns the previous value."""
        p = self.payload(model, name)
        try:
            before = deep_get(p, field_path)
        except (KeyError, IndexError):
            before = None
        deep_set(p, field_path, value, create=create)
        self._save(model, name, p)
        return before

    def remove_field(self, model: str, name: str, field_path: str) -> Any:
        p = self.payload(model, name)
        before = deep_get(p, field_path)
        deep_delete(p, field_path)
        self._save(model, name, p)
        return before

    def append(self, model: str, name: str, field_path: str, value: Any) -> int:
        """Append to a list field. Returns the index of the new item."""
        p = self.payload(model, name)
        lst = deep_get(p, field_path)
        if not isinstance(lst, list):
            raise StoreError(f"{field_path} is not a list field")
        lst.append(value)
        self._save(model, name, p)
        return len(lst) - 1

    def clean(self, model: str, name: str, field_path: str) -> list:
        p = self.payload(model, name)
        lst = deep_get(p, field_path)
        before = list(lst)
        seen, out = set(), []
        for item in lst:
            k = json.dumps(item, sort_keys=True)
            if item in (None, "", [], {}) or k in seen:
                continue
            seen.add(k); out.append(item)
        deep_set(p, field_path, out)
        self._save(model, name, p)
        return before

    def untrack(self, name: str) -> None:
        DocCLI().untrack(SimpleNamespace(doc=name, store=str(self.sp), pythonpath=self.pythonpath))
        self.invalidate()

    def track(self, path: Path, model: str, name: str) -> None:
        model_type, entry, idx = registered_model(self.sp, model, self.pythonpath)
        track_document(self.sp, self.project_root, idx, model_type, entry, path, name, resolve_model_ref, self.pythonpath)
        self.invalidate()
