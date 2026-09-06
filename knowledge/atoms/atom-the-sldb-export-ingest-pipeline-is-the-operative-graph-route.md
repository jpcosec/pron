---
id: atom-the-sldb-export-ingest-pipeline-is-the-operative-graph-route
title: "The sldb export plus ingest pipeline is the operative graph route"
five_wh_one_plus: how
tags:
- system:kgdb
- kind:software
- impl:external
- domain:graph_architecture
- graph:materialization
- cross:sldb_kgdb
provenance: Derived from `source/spec/KGDB_LAYER.md`, verified end-to-end against this repo's store (2026-09-06).
---

# The sldb export plus ingest pipeline is the operative graph route

## Answer

The working pipeline is 'sldb stores semantic-export' producing the sldb_kgdb_semantic_export contract, then 'kgdb ingest-sldb' persisting a networkx graph. It projects store, models, documents, sections, and semantic tags as nodes under the sldb:// id scheme, with has_model/has_document/has_section/tagged_as edges and full source provenance per node. In this repo it yields 1000 nodes from 274 documents.
