---
id: atom-grafo-indice-g-index-graph-and-collision-detection
title: Grafo Indice G / Index Graph and Collision Detection
five_wh_one_plus: what
tags:
- domain:knowledge_representation
- graph:concept
provenance: Derived from current project specs during the spec-alignment pass. Exact per-atom source mapping is pending metadata backfill.
---

# Grafo Indice G / Index Graph and Collision Detection

## Answer

The index graph layer (G in SMG) that organizes dimensions and projections as an inverted index over the fact database. Maintains the transposed matrix M^T of all contexts. If two concepts share identical values in the transposed index, G detects a collision and triggers expand_collision to inject new discriminative dimensions. Enables inverse queries ('which concepts have property X?').
