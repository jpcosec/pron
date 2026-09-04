---
id: atom-knowledge-graph-list-should-provide-fast-snapshot-native-node-inventory-without-semantic-reinterpretation
title: Knowledge graph list should provide fast snapshot-native node inventory without
  semantic reinterpretation
five_wh_one_plus: what
tags:
- system:knowledge
- topic:knowledge_cli
- topic:knowledge_graph
- graph:provenance
provenance: Derived from `knowledge` and `.sldb/runtime/knowledge_graph.kg.json`.
---

# Knowledge graph list should provide fast snapshot-native node inventory without semantic reinterpretation

## Answer

`knowledge graph list` should exist as a fast local inventory of graph nodes taken directly from the snapshot, with optional type filtering, rather than as a heavy traversal command. Its job in the knowledge layer is discoverability of what the graph currently materializes, not inference about what relations ought to exist.
