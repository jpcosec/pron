---
id: atom-graph-endpoint-addressability-requires-semantic-disambiguation
title: Graph-endpoint addressability requires semantic disambiguation
five_wh_one_plus: how
tags:
- system:marcado
- topic:anchoring
provenance: Derived from current project specs during the spec-alignment pass. Exact per-atom source mapping is pending metadata backfill.
---

# Graph-endpoint addressability requires semantic disambiguation

## Answer

Graph-referenced endpoints must have at least 2 classification segments (e.g. rhet:rationale.use_case, not bare rhet:rationale). Numeric-only disambiguators (rhet:rationale.1) are rejected. Single-character suffixes (rhet:evidence.a) are rejected. Generic suffixes like 'thing', 'thing_a', 'node', 'item', 'misc' trigger semantic lint warnings. The _addressability_error and _addressability_lint functions in validation.py enforce these rules.
