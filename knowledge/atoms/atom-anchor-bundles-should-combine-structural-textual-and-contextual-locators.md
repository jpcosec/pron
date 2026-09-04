---
id: atom-anchor-bundles-should-combine-structural-textual-and-contextual-locators
title: Anchor bundles should combine structural, textual, and contextual locators
five_wh_one_plus: how
tags:
  - system:kb
  - topic:anchoring
provenance: Derived from `spec/KB_SYSTEM_SPEC.md` and `spec/LEGACY_EXTRACTION_FROM_HUM_ECOSYSTEM.md` as a synthesis of the recommended hybrid anchoring strategy and the role of anchor bundles in a multi-source KB.
---

# Anchor bundles should combine structural, textual, and contextual locators

## Answer

Anchor bundles should combine structural locators, textual locators, and retrieval context in the same recoverable unit instead of relying on only one anchor style. Structural locators such as pages or section paths help reattach to document shape, textual locators such as exact quotes and surrounding text help reidentify the passage, and contextual locators such as source hashes bind the bundle to the correct artifact version. Combining the three makes validation and re-anchoring more deterministic across heterogeneous source types and after partial structure shifts.
