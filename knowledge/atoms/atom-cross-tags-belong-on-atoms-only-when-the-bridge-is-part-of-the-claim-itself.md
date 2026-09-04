---
id: atom-cross-tags-belong-on-atoms-only-when-the-bridge-is-part-of-the-claim-itself
title: Cross tags belong on atoms only when the bridge is part of the claim itself
five_wh_one_plus: when
tags:
- system:knowledge
- topic:multi_source
- topic:atom_metadata
- cross:deskops_kb
provenance: Derived from `desk/atoms/tag-namespaces.yaml`, `spec/ATOM_METADATA_DOC.md`,
  and `desk/atoms/kb/bootstrap/query/atom-cross-tags-should-mark-bridge-knowledge-between-systems-and-projects.md`.
---

# Cross tags belong on atoms only when the bridge is part of the claim itself

## Answer

`cross:*` belongs in atom tags only when the atom’s thesis is inherently about a bridge across systems, projects, or graph strata. If the atom merely happens to be curated from multiple sources or projects, that crossing should be expressed in provenance and metadata instead of being treated as atom semantics.
