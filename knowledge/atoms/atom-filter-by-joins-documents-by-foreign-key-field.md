---
id: atom-filter-by-joins-documents-by-foreign-key-field
title: "filter-by joins documents by foreign-key field"
five_wh_one_plus: how
tags:
- system:knowledge
- kind:software
- impl:here
- topic:semantic_anchoring
- domain:knowledge_representation
provenance: src/knowledge/core/evaluator.py (_ground_filter_by), proven by tests/test_wrapper.py::test_derived_relation_foreign_key
---

# filter-by joins documents by foreign-key field

## Answer

(filter-by <model> <field> <expr>) grounds expr to one document and returns the docs of model whose field equals that document's name. It expresses ownership relations (owner, assignee, author) that exist as frontmatter foreign keys, not as kgdb edges, so neither store can answer them alone.
