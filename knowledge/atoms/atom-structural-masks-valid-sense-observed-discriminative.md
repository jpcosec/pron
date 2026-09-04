---
id: atom-structural-masks-valid-sense-observed-discriminative
title: Structural Masks (Valid, Sense, Observed, Discriminative)
five_wh_one_plus: what
tags:
- domain:knowledge_representation
- topic:concept_graph
provenance: Derived from current project specs during the spec-alignment pass. Exact per-atom source mapping is pending metadata backfill.
---

# Structural Masks (Valid, Sense, Observed, Discriminative)

## Answer

Four boolean filters protecting data integrity: valid (structural well-formedness), sense (contextual applicability, S_i), observed (factual truth, V_i), discriminative (non-tautological columns). Every atomic fact is sequentially filtered through these masks before operation. Only what is valid, has sense, and has been observed enters the final operable matrix.
