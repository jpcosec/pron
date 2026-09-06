---
id: atom-structuredquery-filters-facets-scope-and-relations
title: "StructuredQuery filters facets, scope, and relations"
five_wh_one_plus: how
tags:
- system:kgdb
- kind:software
- impl:external
- domain:graph_architecture
- graph:retrieval
provenance: Derived from `source/spec/KGDB_LAYER.md`, verified end-to-end against this repo's store (2026-09-06).
---

# StructuredQuery filters facets, scope, and relations

## Answer

A StructuredQuery has 'filters' (facet + field conditions with ops eq/ne/is_null/is_not_null/contains/gt/lt/starts_with), 'scope' (descendant_of, ancestor_of, or node_id_prefix), and 'relations' (edge allow-list with direction) which filters returned edges, not matched nodes. 'contains' is list membership, which is how tag queries work: semantic_tags contains topic:semantic_anchoring returned 99 of 1000 nodes here.
