---
id: atom-drift-checks-are-review-surfaces-not-mutators
title: Drift checks are review surfaces, not mutators
five_wh_one_plus: what
tags: []
provenance: null
---

# Drift checks are review surfaces, not mutators

## Answer

Drift detection emits provenance-backed findings with confidence labels, dedupe keys, and promotion paths (tasks, questions, atoms); accepted/rejected decisions persist in a runtime ledger (.sldb/runtime/self_reflection_decisions.json) and no drift check mutates durable knowledge automatically.
