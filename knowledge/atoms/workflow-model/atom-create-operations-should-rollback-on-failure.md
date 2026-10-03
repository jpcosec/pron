---
id: atom-create-operations-should-rollback-on-failure
title: Create operations should roll back on failure
five_wh_one_plus: how_not
tags:
- system:deskops
- topic:operations
- topic:data-integrity
---

# Create operations should roll back on failure

## Answer

A failed workflow create operation must not leave partial files, orphan tracking records, or half-appended board listings. Each create must either complete fully or restore the prior state. Silent orphan artifacts are knowledge-system failures that erode trust in deskops operations.
