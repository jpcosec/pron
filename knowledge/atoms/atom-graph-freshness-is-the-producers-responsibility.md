---
id: atom-graph-freshness-is-the-producers-responsibility
title: "Graph freshness is the producer's responsibility"
five_wh_one_plus: why
tags:
- system:kgdb
- kind:software
- impl:external
- domain:graph_architecture
- graph:materialization
- cross:knowledge_kgdb
provenance: Derived from `source/spec/KGDB_LAYER.md`, verified end-to-end against this repo's store (2026-09-06).
---

# Graph freshness is the producer's responsibility

## Answer

kgdb has no incremental mutation surface and no freshness check: a stale snapshot answers stale results without warning. The producer must re-run export plus ingest after any store change, and consumers like the knowledge kgdb bridge must compare the snapshot's recorded store hash_a against the live store to warn instead of silently serving old truth.
