---
id: atom-pure-matrices-vs-block-matrices
title: Pure Matrices vs Block Matrices
five_wh_one_plus: what
tags:
- domain:knowledge_representation
- domain:graph_architecture
provenance: Derived from current project specs during the spec-alignment pass. Exact per-atom source mapping is pending metadata backfill.
---

# Pure Matrices vs Block Matrices

## Answer

Pure matrices are dense boolean matrices representing a single isolated context with only its own Li axes, stored per-WiGame in the engine core. Block matrices (omnirepresentacion) unify multiple subcontexts, routing rules, and facts into one topological space for LLM consumption. Pure matrices are for internal storage/computation; block matrices are the I/O interface for stochastic models.
