---
# atom-xxx, unique identifier
id: atom-subagent-runs-are-linked-to-session-logs-by-hash
# Short, descriptive title
title: Subagent runs are linked to session logs by hash
# what | why | how | how_not | when | where | for_whom
five_wh_one_plus: how
# e.g., system:deskops, topic:templates
tags:
- system:deskops
- topic:roles
- topic:evidence
- topic:provenance
# Optional URL or path to the authoritative source of this knowledge
provenance: null
---

# Subagent runs are linked to session logs by hash

## Answer

_Answer the selected 5WH1+ question as one stable knowledge unit._

Every delegated run is reviewable after the fact. pi records each subagent dispatch in the parent session jsonl with agent name and runId; child session logs live at <parent-session-dir>/<runId>/run-N/session.jsonl with a per-entry id/parentId execution tree. The hard linkage rule: the dispatcher records the runId at dispatch time, and the run's result-summary.md must carry run_id, the child session.jsonl path, and its session_sha256 (sha256sum of the file). The hash freezes what the agent did; any later log edit breaks it. run-history.jsonl has no runId and is not a linkage surface.
