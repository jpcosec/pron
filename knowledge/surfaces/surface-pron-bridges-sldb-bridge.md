---
id: surface-pron-bridges-sldb-bridge
system: pron
surface: pron.bridges.sldb_bridge
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
provenance: src/pron/bridges/sldb_bridge.py
---

# pron.bridges.sldb_bridge

## Purpose

Single door to sldb

## How It Works

atom-bridges-are-the-only-doors-to-sldb-and-kgdb: No component outside sldb_bridge and kgdb_bridge may import sldb or kgdb. The sldb bridge uses the real library layer (load_runtime_documents, resolve_model_ref, docs/fields ops) and never reimplements search or shells out to the sldb CLI. The kgdb bridge validates snapshots against GraphSnapshot and warns on stale snapshots instead of returning silently outdated results.

## Commands

SldbBridge
SldbBridge.documents(self, include_linked: bool=False) -> list | All tracked RuntimeDocuments (payload already extracted).
SldbBridge.documents_of_model(self, model_name: str) -> list | Tracked documents of one model.
SldbBridge.store_hash(self) -> str | Current hash_a of the store (freshness token for session/graph).
SldbBridge.model_names(self) -> list[str] | Names of all registered models.
SldbBridge.filter_where(self, docs: list, expression: str) -> list | Filter documents with sldb's real where engine.

Supports: has(field) | "needle" in field | field ~ "regex" |
field = value | field != value (DocumentFilter grammar).
SldbBridge.by_semantic_tag(self, tag: str) -> list | Documents carrying a semantic tag, via the semantic index.
SldbBridge.registered_model_ref(self, model_name: str) -> str | None | Map a registered model name to its module:Class ref, via the store index.
SldbBridge.resolve_model(self, ref: str) | Resolve a module:Class model ref at the bridge door.
SldbBridge.create_doc(self, payload: dict, model_type: type, name: str, doc_path: Path) -> None | Render, validate and track one new document (library-level docs create).
bridge_for(root: str, pythonpath: str | None=None) -> SldbBridge | Per-invocation cached bridge.
