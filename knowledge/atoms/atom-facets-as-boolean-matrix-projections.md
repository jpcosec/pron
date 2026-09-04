---
id: atom-facets-as-boolean-matrix-projections
title: Facets as Boolean Matrix Projections
five_wh_one_plus: what
tags:
- domain:knowledge_representation
- domain:graph_architecture
provenance: Derived from current project specs during the spec-alignment pass. Exact per-atom source mapping is pending metadata backfill.
---

# Facets as Boolean Matrix Projections

## Answer

A Facet (RoutingProjection) projects subjects from one WiGame context into another via boolean matrix multiplication. It is a concrete RoutingProjection matrix where rows belong to the source WiGame and columns to the target WiGame. True entries mark that a source subject projects to a target subject, enabling cross-context navigation and composition (e.g., W_animales x r_proyeccion x W_caninos).
