---
id: atom-knowledge-graph-show-should-expose-raw-node-identity-semantics-path-and-edge-payloads-for-auditability
title: Knowledge graph show should expose raw node identity semantics path and edge
  payloads for auditability
five_wh_one_plus: how
tags:
- system:knowledge
- topic:knowledge_cli
- topic:knowledge_graph
- graph:provenance
provenance: Derived from `knowledge` and `spec/GRAPH_ARCHITECTURE.md`.
---

# Knowledge graph show should expose raw node identity semantics path and edge payloads for auditability

## Answer

`knowledge graph show` should expose a node’s identity, type, semantic label, path, and raw edge payloads without trying to reinterpret the underlying claim. In the knowledge layer, this supports auditability and debugging of graph materialization rather than replacing the original atom or source document.
