---
id: atom-bridges-are-the-only-doors-to-sldb-and-kgdb
title: "Bridges are the only doors to sldb and kgdb"
five_wh_one_plus: how_not
tags:
- system:knowledge
- kind:concept
- impl:here
- topic:semantic_anchoring
- domain:system_architecture
- cross:knowledge_sldb
provenance: Derived from `source/spec/KNOWLEDGE_COMPONENTS.md`.
---

# Bridges are the only doors to sldb and kgdb

## Answer

No component outside sldb_bridge and kgdb_bridge may import sldb or kgdb. The sldb bridge uses the real library layer (load_runtime_documents, resolve_model_ref, docs/fields ops) and never reimplements search or shells out to the sldb CLI. The kgdb bridge validates snapshots against GraphSnapshot and warns on stale snapshots instead of returning silently outdated results.
