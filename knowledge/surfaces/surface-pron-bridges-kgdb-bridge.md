---
id: surface-pron-bridges-kgdb-bridge
system: pron
surface: pron.bridges.kgdb_bridge
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
provenance: src/pron/bridges/kgdb_bridge.py
---

# pron.bridges.kgdb_bridge

## Purpose

Single door to kgdb

## How It Works

atom-bridges-are-the-only-doors-to-sldb-and-kgdb: No component outside sldb_bridge and kgdb_bridge may import sldb or kgdb. The sldb bridge uses the real library layer (load_runtime_documents, resolve_model_ref, docs/fields ops) and never reimplements search or shells out to the sldb CLI. The kgdb bridge validates snapshots against GraphSnapshot and warns on stale snapshots instead of returning silently outdated results.

atom-graph-freshness-is-the-producers-responsibility: kgdb has no incremental mutation surface and no freshness check: a stale snapshot answers stale results without warning. The producer must re-run export plus ingest after any store change, and consumers like the knowledge kgdb bridge must compare the snapshot's recorded store hash_a against the live store to warn instead of silently serving old truth.

## Commands

KgdbBridge
KgdbBridge.available(self) -> bool | Whether a materialized graph exists.
KgdbBridge.snapshot_store_hash(self) -> str | hash_a recorded at export time, for freshness comparison.
KgdbBridge.is_stale(self, live_store_hash: str) -> bool | True when the snapshot was built from a different store state.
KgdbBridge.node(self, node_id: str) -> dict | None | One node's schema payload by id.
KgdbBridge.edges_from(self, node_id: str, relation: str | None=None) -> list[dict] | Outgoing edges of a node, optionally filtered by relation_type.
KgdbBridge.edges_to(self, node_id: str, relation: str | None=None) -> list[str] | Ids of nodes with an edge pointing at node_id (incoming).
KgdbBridge.document_node_id(self, model: str, name: str) -> str | Canonical sldb:// id for a tracked document.
