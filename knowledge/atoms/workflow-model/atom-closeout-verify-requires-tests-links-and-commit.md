---
id: atom-closeout-verify-requires-tests-links-and-commit
title: Closeout verify requires tests links and commit
five_wh_one_plus: how
tags:
- system:deskops
- topic:closeout
- topic:workflow
- topic:materialization
provenance: null
---

# Closeout verify requires tests links and commit

## Answer

Before the tool-made closing commit, `deskops closeout verify` should fail unless the task carries resolvable test evidence, changed-file atom or materialization coverage (or a routed follow-up when a file still lacks a live link), and commit evidence. Changed generated artifacts with a live sibling source must also declare `source_atoms` or `provenance`; path-pair drift comparison stays out of scope for this gate.
