---
id: atom-knowledge-cli-should-separate-knowledge-operations-from-operational-workflow
title: Knowledge CLI should separate knowledge operations from operational workflow
five_wh_one_plus: why
tags:
- system:knowledge
- system:deskops
- topic:knowledge_cli
- topic:workflow_separation
provenance: Derived from `spec/source_apps/deskops.md`, `spec/DESKOPS_FOR_KNOWLEDGE_MANAGEMENT.md`,
  `spec/ATOM_METADATA_DOC.md`, and the local `knowledge` CLI implementation.
---

# Knowledge CLI should separate knowledge operations from operational workflow

## Answer

The `knowledge` CLI should separate knowledge operations from operational workflow so atoms, metadata, and graph inspection can evolve without inheriting task, board, ritual, or inbox behavior. It preserves the useful knowledge-facing affordances of `deskops` while dropping the operational surface that does not belong to the knowledge layer.
