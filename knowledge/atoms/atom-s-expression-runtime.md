---
id: atom-s-expression-runtime
title: S-Expression Runtime
five_wh_one_plus: how
tags:
- domain:knowledge_representation
- domain:graph_architecture
provenance: Derived from current project specs during the spec-alignment pass. Exact per-atom source mapping is pending metadata backfill.
---

# S-Expression Runtime

## Answer

Canonical command interface with operations: (check) evaluate truth/sense of a proposition, (assert) add a true fact, (create symbol/relation/li/wigame) define entities, (ingest) register a proposition, (return facts) query stored facts. The runtime resolves commands against the LogicalSystem, validates against WiGame sense matrices, and returns structured OperationResult with status, sinn, and payload.
