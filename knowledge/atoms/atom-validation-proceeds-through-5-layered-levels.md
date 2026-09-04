---
id: atom-validation-proceeds-through-5-layered-levels
title: Validation proceeds through 5 layered levels
five_wh_one_plus: how
tags:
- system:marcado
- topic:anchoring
provenance: Derived from current project specs during the spec-alignment pass. Exact per-atom source mapping is pending metadata backfill.
---

# Validation proceeds through 5 layered levels

## Answer

Level 1 Syntax: checks matching open/close markers, valid marker grammar, no mixed namespaces. Level 2 Namespace: validates namespace-specific rules like crossing policies. Level 3 Addressability: checks graph-referenced markers are unique and semantically disambiguated. Level 4 Graph: validates every edge from/to target exists and edge types are valid. Level 5 Semantic Lint: weak names, vague paths, duplicate semantics (non-blocking warnings). Blocking errors fail validation; lint warnings do not.
