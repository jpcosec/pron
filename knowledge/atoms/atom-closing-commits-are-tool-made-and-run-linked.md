---
# atom-xxx, unique identifier
id: atom-closing-commits-are-tool-made-and-run-linked
# Short, descriptive title
title: Closing commits are tool-made and run-linked
# what | why | how | how_not | when | where | for_whom
five_wh_one_plus: how_not
# e.g., system:deskops, topic:templates
tags:
- system:deskops
- topic:roles
- topic:closeout
- topic:provenance
# Optional URL or path to the authoritative source of this knowledge
provenance: null
---

# Closing commits are tool-made and run-linked

## Answer

_Answer the selected 5WH1+ question as one stable knowledge unit._

A task closing commit must never depend on agent discretion. It is created by 'deskops closeout commit --task <id> --run-dir <runs/subagents/dir>', which refuses to run without the required evidence files, writes run.yaml (run_id, session, session_sha256) into the commit, embeds Task-Id/Run-Dir/Run-Id/Session-Sha256 git trailers, and appends the resulting commit hash to runs/subagents/index.jsonl. Commit-to-run linkage travels in the immutable commit message; run-to-commit linkage lives in the append-only index. Do not handcraft closing commits with plain git commit, and do not treat a green test run as closeout without the linked commit.
