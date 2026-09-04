---
id: atom-omnirepresentacion-block-matrix-for-llm-integration
title: Omnirepresentacion / Block Matrix for LLM Integration
five_wh_one_plus: what
tags:
- domain:knowledge_representation
- topic:concept_graph
provenance: Derived from current project specs during the spec-alignment pass. Exact per-atom source mapping is pending metadata backfill.
---

# Omnirepresentacion / Block Matrix for LLM Integration

## Answer

A generalized Block Matrix that unifies subcontexts, routing rules, and facts for LLM consumption. Structure: diagonal m x m (WC_i context switches), cross-blocks m x n (routing/belonging matrices with Don't Cares), bottom-right n x n (empirical truth matrix). Serves as unified I/O format for neural networks to ingest and generate logical relations across the full graph.
