---
# routine-xxx
id: routine-task-implement-knowledge-anchor-add
# active | archived
status: active
# Initial node identifier
entrypoint: checklist-task-implement-knowledge-anchor-add-execution-ready
# Ordered or grouped primitive identifiers
decomposition:
- checklist-task-implement-knowledge-anchor-add-execution-ready
- operator-task-implement-knowledge-anchor-add-activate
- checklist-task-implement-knowledge-anchor-add-testing-ready
- operator-task-implement-knowledge-anchor-add-ready-for-testing
- checklist-task-implement-knowledge-anchor-add-closeout-ready
- operator-task-implement-knowledge-anchor-add-close
# Edge identifiers composing the graph
edges:
- edge-task-implement-knowledge-anchor-add-execution-to-activate
- edge-task-implement-knowledge-anchor-add-activate-to-testing
- edge-task-implement-knowledge-anchor-add-testing-to-ready
- edge-task-implement-knowledge-anchor-add-ready-to-closeout
- edge-task-implement-knowledge-anchor-add-closeout-to-close
- edge-task-implement-knowledge-anchor-add-close-to-complete
# Terminal node identifiers
terminal_nodes:
- complete
# e.g., system:deskops
tags:
- workspace:desk
- primitive:routine
---

# Routine for Implement knowledge anchor add

## Summary

_Summarize what this routine does and how its nodes fit together._

Actionable routine for Implement knowledge anchor add.
