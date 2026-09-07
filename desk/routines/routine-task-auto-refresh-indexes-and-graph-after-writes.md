---
# routine-xxx
id: routine-task-auto-refresh-indexes-and-graph-after-writes
# active | archived
status: active
# Initial node identifier
entrypoint: checklist-task-auto-refresh-indexes-and-graph-after-writes-execution-ready
# Ordered or grouped primitive identifiers
decomposition:
- checklist-task-auto-refresh-indexes-and-graph-after-writes-execution-ready
- operator-task-auto-refresh-indexes-and-graph-after-writes-activate
- checklist-task-auto-refresh-indexes-and-graph-after-writes-testing-ready
- operator-task-auto-refresh-indexes-and-graph-after-writes-ready-for-testing
- checklist-task-auto-refresh-indexes-and-graph-after-writes-closeout-ready
- operator-task-auto-refresh-indexes-and-graph-after-writes-close
# Edge identifiers composing the graph
edges:
- edge-task-auto-refresh-indexes-and-graph-after-writes-execution-to-activate
- edge-task-auto-refresh-indexes-and-graph-after-writes-activate-to-testing
- edge-task-auto-refresh-indexes-and-graph-after-writes-testing-to-ready
- edge-task-auto-refresh-indexes-and-graph-after-writes-ready-to-closeout
- edge-task-auto-refresh-indexes-and-graph-after-writes-closeout-to-close
- edge-task-auto-refresh-indexes-and-graph-after-writes-close-to-complete
# Terminal node identifiers
terminal_nodes:
- complete
# e.g., system:deskops
tags:
- workspace:desk
- primitive:routine
---

# Routine for Auto-refresh indexes and graph after writes

## Summary

_Summarize what this routine does and how its nodes fit together._

Actionable routine for Auto-refresh indexes and graph after writes.
