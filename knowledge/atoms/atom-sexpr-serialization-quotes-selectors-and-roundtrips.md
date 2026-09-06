---
id: atom-sexpr-serialization-quotes-selectors-and-roundtrips
title: "S-expression serialization quotes selectors and roundtrips"
five_wh_one_plus: how
tags:
- system:knowledge
- kind:concept
- impl:here
- topic:semantic_anchoring
- domain:knowledge_representation
provenance: Derived from `source/spec/KNOWLEDGE_COMPONENTS.md`, section 'Decisiones cerradas'.
---

# S-expression serialization quotes selectors and roundtrips

## Answer

The canonical s-expression format is a small lisp subset: symbols are unquoted, selectors are always double-quoted strings with escaped inner quotes, options are trailing :keyword-symbol pairs, and refs take three shapes: (docs model), (doc model "selector"), (rel relation expr). Every valid expression roundtrips: parse(serialize(e)) equals e, and Meaning-to-Surface serialization uses the canonical noun-first order.
