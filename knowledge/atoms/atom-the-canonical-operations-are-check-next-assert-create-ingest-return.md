---
id: atom-the-canonical-operations-are-check-next-assert-create-ingest-return
title: The canonical operations are check, next, assert, create, ingest, return
five_wh_one_plus: what
tags:
- system:knowledge
- domain:knowledge_representation
- kind:concept
- impl:here
- topic:semantic_anchoring
- entity:cli_command
provenance: Derived from `source/spec/KNOWLEDGE_CORE_SEMANTIC_ANCHORING.md` (knowledge core spec), inspired by SHRDLU-style world-grounded resolution and the existing SMG / s-expression runtime atoms.
---

# The canonical operations are check, next, assert, create, ingest, return

## Answer

The core operation set is: check (evaluate or read without mutation), next (the next element by state, order defined by the model), assert (add a fact as true), create (define entities: symbols, relations, models, docs), ingest (register a proposition or document), and return (query stored facts). Reads project payloads from sldb/kgdb; writes go through sldb with provenance.
