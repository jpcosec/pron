---
id: atom-searchvector
title: SearchVector
five_wh_one_plus: what
tags:
- domain:knowledge_representation
- domain:graph_architecture
provenance: Derived from current project specs during the spec-alignment pass. Exact per-atom source mapping is pending metadata backfill.
---

# SearchVector

## Answer

A local query vector inside a WiGame that marks which terms on the axis_b (column side) are being requested. It is evaluated against Vi (truth matrix) while Si (sense matrix) prevents malformed matches. Materialized as a single-row BooleanMatrix. Answers: what am I looking for inside this game?
