---
id: atom-anchor-ref-is-a-typed-string-with-a-scheme-per-kind
title: "Anchor ref is a typed string with a scheme per kind"
five_wh_one_plus: how
tags:
- system:knowledge
- kind:concept
- impl:here
- topic:semantic_anchoring
- domain:knowledge_representation
- entity:anchor
provenance: Derived from `source/spec/KNOWLEDGE_COMPONENTS.md`, section 'Decisiones cerradas'.
---

# Anchor ref is a typed string with a scheme per kind

## Answer

AnchorDoc.ref is a single string with a kind-specific scheme validated by regex: model:<Name>, doc:<name>, edge:<relation_type>[:direction], op:<function>, and fields:<f1,f2> or view:<name> for projections. A typed string instead of a dict keeps frontmatter legible and validation simple; complex resolution lives in the evaluator, not in the anchor.
