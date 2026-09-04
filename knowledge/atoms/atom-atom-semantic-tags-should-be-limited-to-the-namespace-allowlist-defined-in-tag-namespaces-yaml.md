---
id: atom-atom-semantic-tags-should-be-limited-to-the-namespace-allowlist-defined-in-tag-namespaces-yaml
title: Atom semantic tags should be limited to the namespace allowlist defined in
  tag-namespaces.yaml
five_wh_one_plus: what
tags:
- system:knowledge
- entity:atom
- entity:metadata_registry
- topic:atom_metadata
provenance: Derived from `desk/atoms/tag-namespaces.yaml` and the local `knowledge`
  CLI implementation.
---

# Atom semantic tags should be limited to the namespace allowlist defined in tag-namespaces.yaml

## Answer

Atom-side semantic tags should come only from the namespace families that are explicitly curated in `desk/atoms/tag-namespaces.yaml`. That keeps retrieval semantics stable and prevents governance namespaces from creeping back into atom frontmatter just because they match the generic `namespace:value` syntax.
