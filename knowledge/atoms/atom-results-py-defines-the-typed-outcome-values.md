---
id: atom-results-py-defines-the-typed-outcome-values
title: "results.py defines the typed outcome values"
five_wh_one_plus: where
tags:
- system:knowledge
- kind:software
- impl:here
- topic:semantic_anchoring
- domain:system_architecture
provenance: src/knowledge/core/results.py
---

# results.py defines the typed outcome values

## Answer

src/knowledge/core/results.py defines Resolved, Ambiguous, Missing, SemanticError, and OperationResult as frozen dataclasses. They are returned as plain values across components; to_dict projects any of them for rendering. Exceptions are reserved for bugs.
