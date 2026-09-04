---
id: atom-relation-algebra
title: Relation Algebra
five_wh_one_plus: what
tags:
- domain:knowledge_representation
- domain:graph_architecture
provenance: Derived from current project specs during the spec-alignment pass. Exact per-atom source mapping is pending metadata backfill.
---

# Relation Algebra

## Answer

Each Relation declares explicit algebraic properties (transitive, symmetric/commutative, associative, distributive) via a RelationAlgebra profile. The engine uses these flags to auto-infer closure facts (e.g., transitive inference: (R a b) and (R b c) implies (R a c)) and canonical coordinate pairs for commutative relations.
