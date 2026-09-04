---
id: atom-two-gates-model-s-i-sense-v-i-truth
title: Two Gates Model (S_i Sense, V_i Truth)
five_wh_one_plus: how
tags:
- domain:knowledge_representation
- topic:concept_graph
provenance: Derived from current project specs during the spec-alignment pass. Exact per-atom source mapping is pending metadata backfill.
---

# Two Gates Model (S_i Sense, V_i Truth)

## Answer

The separation of semantic applicability (Sense matrix S_i) from factual truth (Truth matrix V_i) in each context W_i. W* = V_i AND S_i -- the operational projection is the intersection of truth and sense. A proposition must first be applicable (S_i[a,b]=1) before its truth value (V_i[a,b]) is evaluated. This prevents confusing 'false' with 'not applicable'.
