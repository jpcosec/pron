---
id: atom-metadata-registry-records-should-be-the-canonical-query-surface-for-governance-facets
title: Metadata registry records should be the canonical query surface for governance
  facets
five_wh_one_plus: why
tags:
- system:knowledge
- entity:metadata_registry
- topic:query
- topic:atom_metadata
provenance: Derived from `metadata/atoms/atom-metadata-registry.yaml`, `spec/ATOM_METADATA_DOC.md`,
  and the local `knowledge` CLI metadata commands.
---

# Metadata registry records should be the canonical query surface for governance facets

## Answer

Governance queries such as which atoms are bootstrap, which are source-file-derived, or which still need stronger grounding should resolve against metadata registry records rather than atom tags alone. That keeps evidentiary and editorial filtering explicit without polluting claim-level retrieval semantics.
