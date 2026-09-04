---
# atom-xxx, unique identifier
id: atom-role-tool-boundaries-and-evidence-surface
# Short, descriptive title
title: Role tool boundaries and evidence surface
# what | why | how | how_not | when | where | for_whom
five_wh_one_plus: how_not
# e.g., system:deskops, topic:templates
tags:
- system:deskops
- topic:roles
- topic:boundaries
# Optional URL or path to the authoritative source of this knowledge
provenance: null
---

# Role tool boundaries and evidence surface

## Answer

_Answer the selected 5WH1+ question as one stable knowledge unit._

Hard boundaries are tool-enforced, not prompt-only. Supervisor and tester installed agents run with tool allowlist 'read, grep, find, ls, bash' and no edit/write tools; bash is restricted by prompt to read-side CLI (deskops, sldb, git status/log/diff, pytest) and must not edit files through redirection or scripts. The executor is the only role that writes implementation code, including tests; if the tester finds missing or stale tests it reports them in result-summary.md and hands back to the executor. Executor and tester annotate on a shared evidence surface under runs/subagents/<run-dir>/ (board.txt, task.txt, next.txt, graph.txt, git-status.txt, result-summary.md, validation.log); the supervisor reviews that surface and never accepts chat-only handoffs. Do not rely on green exit codes or prompt promises as boundaries.
