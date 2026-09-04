---
id: atom-regex-valid-metadata-namespaces-should-still-be-excluded-from-atom-tags
title: Regex-valid metadata namespaces should still be excluded from atom tags
five_wh_one_plus: why
tags:
- system:knowledge
- entity:atom
- topic:atom_metadata
- topic:tag_policy
provenance: Derived from `knowledge`, `spec/ATOM_METADATA_DOC.md`, and `desk/atoms/tag-namespaces.yaml`.
---

# Regex-valid metadata namespaces should still be excluded from atom tags

## Answer

A tag being syntactically valid is not enough to make it atom-semantic. Namespaces like `project:*`, `source:*`, `source_kind:*`, `grounding:*`, `scope:*`, `role:*`, `phase:*`, `bootstrap:*`, `method:*`, `status:*`, and `legacy:*` describe the atom’s curation state or origin, so they belong in metadata even though the CLI can parse them as namespaced tags.
