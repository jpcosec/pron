---
id: atom-commands-follow-the-smg-model-surface-meaning-graph
title: "Commands follow the SMG model: surface, meaning, graph"
five_wh_one_plus: how
tags:
- system:knowledge
- domain:knowledge_representation
- kind:concept
- impl:pending
- topic:semantic_anchoring
- topic:composition
- cross:smg_command_layer
provenance: Derived from `source/spec/KNOWLEDGE_CORE_SEMANTIC_ANCHORING.md` (knowledge core spec), inspired by SHRDLU-style world-grounded resolution and the existing SMG / s-expression runtime atoms.
---

# Commands follow the SMG model: surface, meaning, graph

## Answer

A command has three layers: Surface (the typed text, e.g. 'user juanito check preferences', reversible syntactic sugar), Meaning (the s-expression it desugars to, e.g. (check (rel preferences (doc user "juanito")))), and Graph (the sldb/kgdb referents each symbol resolves to). Surface-to-Meaning is deterministic positional desugaring, not free NLP; Meaning-to-Graph resolves each symbol through its anchor.
