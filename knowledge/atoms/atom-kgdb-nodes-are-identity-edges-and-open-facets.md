---
id: atom-kgdb-nodes-are-identity-edges-and-open-facets
title: "KGDB nodes are identity, edges, and open facets"
five_wh_one_plus: what
tags:
- system:kgdb
- kind:software
- impl:external
- domain:graph_architecture
- graph:structure
provenance: Derived from `source/spec/KGDB_LAYER.md`, verified end-to-end against this repo's store (2026-09-06).
---

# KGDB nodes are identity, edges, and open facets

## Answer

A KnowledgeNode is a mandatory identity {node_id, node_type}, a list of directed edges {target_id, relation_type, metadata}, and optional open facets (semantics, ast, io_ports, compliance, adr, test_map, git, source) with extra=allow. node_type and relation_type are downstream-defined vocabulary tokens: kgdb imposes no ontology.
