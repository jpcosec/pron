---
id: atom-sexpr-py-is-the-dependency-free-meaning-kernel
title: "sexpr.py is the dependency-free Meaning kernel"
five_wh_one_plus: where
tags:
- system:knowledge
- kind:software
- impl:here
- topic:semantic_anchoring
- domain:knowledge_representation
provenance: src/knowledge/core/sexpr.py
---

# sexpr.py is the dependency-free Meaning kernel

## Answer

src/knowledge/core/sexpr.py implements parse and serialize for the Meaning layer: Symbol, Keyword, quoted strings with escapes, numbers, and nested lists. It imports nothing from the project, raises SexprError only for malformed text, and guarantees parse(serialize(e)) == e.
