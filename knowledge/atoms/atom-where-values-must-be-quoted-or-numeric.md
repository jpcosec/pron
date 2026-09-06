---
id: atom-where-values-must-be-quoted-or-numeric
title: "Where comparison values must be quoted or numeric"
five_wh_one_plus: how_not
tags:
- system:knowledge
- kind:software
- impl:here
- topic:semantic_anchoring
- domain:retrieval
- cross:knowledge_sldb
provenance: sldb src/sldb/store/query_engine/filter.py (_eval_compare), discovered by tests/test_wrapper.py::test_where_uses_sldb_engine
---

# Where comparison values must be quoted or numeric

## Answer

sldb's DocumentFilter compare grammar only matches field = "value" or numeric literals; status = active silently matches nothing because the expression fails every rule and returns False. Write status = \"active\". A where filter returning an empty set unexpectedly is a signal of a malformed expression.
