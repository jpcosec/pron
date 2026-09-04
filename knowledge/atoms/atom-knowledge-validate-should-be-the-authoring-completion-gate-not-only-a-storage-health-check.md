---
id: atom-knowledge-validate-should-be-the-authoring-completion-gate-not-only-a-storage-health-check
title: Knowledge validate should be the authoring completion gate, not only a storage
  health check
five_wh_one_plus: why
tags:
- system:knowledge
- entity:atom
- topic:knowledge_cli
- topic:validation
provenance: Derived from `knowledge`, `spec/atom_quality/ATOM_AUTHORING_PROCEDURE.md`,
  and `spec/atom_quality/ATOM_QUALITY_CHECKLIST.md`.
---

# Knowledge validate should be the authoring completion gate, not only a storage health check

## Answer

`knowledge validate` should be the authoring completion gate, not only a storage health check, because a finished atom needs both repository integrity and content-level acceptability. The current flow already proves store and graph consistency, but the intended UX should eventually extend that gate to atom-quality checks such as missing answer blocks, empty tags, absent provenance, and other checklist failures.
