---
id: atom-kgdb-bridge-py-guards-staleness-before-serving-graph-reads
title: "kgdb_bridge.py guards staleness before serving graph reads"
five_wh_one_plus: where
tags:
- system:knowledge
- kind:software
- impl:here
- topic:semantic_anchoring
- domain:system_architecture
- cross:knowledge_kgdb
provenance: src/knowledge/bridges/kgdb_bridge.py
---

# kgdb_bridge.py guards staleness before serving graph reads

## Answer

src/knowledge/bridges/kgdb_bridge.py loads .sldb/runtime/knowledge.nx.json, reads the store hash recorded at export time, and is_stale() compares it with the live hash so rel traversals refuse stale answers with a reproject instruction. It exposes node, edges_from, edges_to, and document_node_id.
