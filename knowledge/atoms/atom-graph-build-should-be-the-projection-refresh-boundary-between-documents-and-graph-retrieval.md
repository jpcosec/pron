---
id: atom-graph-build-should-be-the-projection-refresh-boundary-between-documents-and-graph-retrieval
title: Graph build should be the projection refresh boundary between documents and
  graph retrieval
five_wh_one_plus: how
tags:
- system:knowledge
- system:kgdb
- topic:knowledge_graph
- graph:provenance
- layer:graph_provenance
provenance: Derived from `knowledge`, `spec/source_apps/kgdb.md`, and `spec/GRAPH_ARCHITECTURE.md`.
---

# Graph build should be the projection refresh boundary between documents and graph retrieval

## Answer

The `knowledge graph build` command should be treated as the refresh boundary that materializes a new queryable graph projection from the document corpus, not as a new source of truth. Documents stay primary, while the graph becomes the refreshed retrieval surface for lineage and support queries.
