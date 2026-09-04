---
id: atom-semantic-namespaces-define-independent-interpretation-rules
title: Semantic namespaces define independent interpretation rules
five_wh_one_plus: what
tags:
- system:marcado
- topic:anchoring
- domain:knowledge_representation
provenance: Derived from current project specs during the spec-alignment pass. Exact per-atom source mapping is pending metadata backfill.
---

# Semantic namespaces define independent interpretation rules

## Answer

Each namespace (struct, sem, rhet, arg, proc, prag) defines its own projection type, crossing policy, and addressability rules. struct forbids crossing and projects a tree. sem allows crossing and projects a taxonomy. rhet allows crossing, requires addressable nodes, and projects a graph. arg projects an argument graph, proc a procedural dependency graph, and prag labels or graphs for speech-act intent. The same marker syntax produces different graph logic depending on namespace.
