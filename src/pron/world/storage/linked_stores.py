"""The stores a world reads (spec 01 §Un mundo en varios stores): the local .sldb and the
stores linked into it, by name, and the sldb operation that spans all of them (spec 02).

This is the base every other layer of `pron.world.store.Store` stands on: it knows where
each store lives, never what a store holds.
"""

from __future__ import annotations

import sys
from pathlib import Path

from sldb.api import StoreUpdateReport, link_store, open_store, update_store_indexes
from sldb.core.exceptions import SLDBStoreError
from sldb.store import documents_hash
from sldb.store.io import load_store_index
from sldb.store.layout import project_root as _project_root, store_exists
from sldb.store.runtime_cache import new_operation as _sldb_new_operation

from pron.kernel.ids import LOCAL, is_local
from pron.world.store_error import StoreError


class LinkedStores:
    """The local store and the stores linked into it, by name."""

    def __init__(self, root: str | Path, pythonpath: str | None = None) -> None:
        self.root = Path(root).resolve()
        location = open_store(self.root / ".sldb")
        self.sp, self.project_root = location.store_path, location.project_root
        self.pythonpath = pythonpath or str(self.root)

    def begin_operation(self) -> None:
        """Start one sldb operation over this store and every linked one.

        sldb re-checks the document files once per operation (PLAN 15 capa 6), and until
        now an operation started only here, in `__init__`: a long-lived World never
        started another one, so a markdown edited by hand or a document written by
        another process (`sldb fields update`, `sldb docs track`) stayed invisible to
        every later read. One pron request is one operation: call this at the start of a
        turn, an eval or a payload read, never inside the read methods themselves (they
        run several times per request; re-checking there would re-stat every file on
        every internal call)."""
        _sldb_new_operation(self.sp)
        documents_hash.new_operation(self.sp)
        for linked in self.linked().values():
            if not store_exists(linked):
                continue
            _sldb_new_operation(linked)
            documents_hash.new_operation(linked)

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
        """Link another world's store under a name (sldb stores add). False when already linked;
        a root that holds no store is refused."""
        if name in self.linked():
            return False
        try:
            link_store(self.sp, Path(other_root).resolve() / ".sldb", name)
        except SLDBStoreError as exc:
            raise StoreError(str(exc)) from exc
        return True

    def store_index(self, store: str | None = LOCAL):
        return load_store_index(self.sp_of(store))

    def update_index(self, store: str | None = LOCAL) -> StoreUpdateReport:
        """sldb `stores update` over one store: re-read and re-hash every tracked file. What
        it had to skip (a model that no longer imports, a file gone) is said on stderr."""
        report = update_store_indexes(self.sp_of(store), self.pythonpath)
        if report.skipped_models:
            print(
                f"Skipped broken models: {', '.join(report.skipped_models)}",
                file=sys.stderr,
            )
        if report.skipped_documents:
            print(
                f"Skipped missing documents: {', '.join(report.skipped_documents)}",
                file=sys.stderr,
            )
        return report
