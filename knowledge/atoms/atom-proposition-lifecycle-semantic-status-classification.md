---
id: atom-proposition-lifecycle-semantic-status-classification
title: Proposition Lifecycle / Semantic Status Classification
five_wh_one_plus: how
tags:
- domain:knowledge_representation
- topic:concept_graph
provenance: Derived from current project specs during the spec-alignment pass. Exact per-atom source mapping is pending metadata backfill.
---

# Proposition Lifecycle / Semantic Status Classification

## Answer

The 5-status lifecycle: Unvalidated -> Unsinnig (structural validation fail, S_i=0) -> Sinnlos (tautology: forall o, V_i[o,p]=1, or contradiction: forall o, V_i[o,p]=0) -> Sinnvoll (true/false, S_i=1 and V_i in {0,1}). Transitions are guarded by matrix conditions. This operationalizes the Tractarian distinction between meaningful, empty, and absurd propositions.
