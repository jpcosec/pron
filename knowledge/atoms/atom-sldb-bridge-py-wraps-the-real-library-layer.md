---
id: atom-sldb-bridge-py-wraps-the-real-library-layer
title: "sldb_bridge.py wraps the real sldb library layer"
five_wh_one_plus: where
tags:
- system:knowledge
- kind:software
- impl:here
- topic:semantic_anchoring
- domain:system_architecture
- cross:knowledge_sldb
provenance: src/knowledge/bridges/sldb_bridge.py
---

# sldb_bridge.py wraps the real sldb library layer

## Answer

src/knowledge/bridges/sldb_bridge.py is the single sldb import point: load_runtime_documents for tracked docs, store_hash from store_index.yaml, filter_where delegating to sldb's DocumentFilter (has/contains/regex/compare), and by_semantic_tag over indexed tags. It never shells out to the sldb CLI for reads.
