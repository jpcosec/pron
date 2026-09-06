---
id: atom-misnamed-query-fields-silently-match-everything
title: "Misnamed query fields silently match everything"
five_wh_one_plus: how_not
tags:
- system:kgdb
- kind:software
- impl:external
- domain:graph_architecture
- graph:retrieval
provenance: Derived from `source/spec/KGDB_LAYER.md`, verified end-to-end against this repo's store (2026-09-06).
---

# Misnamed query fields silently match everything

## Answer

Pydantic ignores unknown fields, so a query written with a wrong field name (facet_filters instead of filters) validates cleanly and returns the entire graph with no error. Always verify a query discriminates before trusting its results; a full-graph response to a filtered query is a signal of a malformed query, not a rich graph.
