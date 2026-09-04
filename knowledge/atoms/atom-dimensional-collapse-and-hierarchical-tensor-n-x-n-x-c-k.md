---
id: atom-dimensional-collapse-and-hierarchical-tensor-n-x-n-x-c-k
title: Dimensional Collapse and Hierarchical Tensor (N x N x C^k)
five_wh_one_plus: how
tags:
- domain:knowledge_representation
- domain:graph_architecture
provenance: Derived from current project specs during the spec-alignment pass. Exact per-atom source mapping is pending metadata backfill.
---

# Dimensional Collapse and Hierarchical Tensor (N x N x C^k)

## Answer

Reducing tensor dimensionality via boolean aggregation for hierarchical routing. A high-order tensor is collapsed to lower dimensions by boolean matrix multiplication (e.g., W = V x V^T for similarity). The hierarchical tensor N x N x C1 x C2 x ... x Ck adds a dimension per abstraction level. Each upper dimension selects a slice in the next, enabling recursive context navigation.
