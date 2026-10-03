---
id: atom-desk-test-root-precedence-is-explicit
title: Desk test root precedence is explicit
five_wh_one_plus: how
tags:
- system:deskops
- topic:config
- topic:testing
- topic:cli
---

# Desk test root precedence is explicit

## Answer

When deskops resolves a project desk root for mutating or test-oriented CLI work, precedence is authoritative and fixed: an explicit CLI root flag wins first, then `DESKOPS_TEST_ROOT`, then `desk/config.local.json`, then tracked `desk/config.json`, then built-in defaults. The project-local config loader must merge `config.json` before `config.local.json`, including nested `versions`, so machine-local sandbox overrides never erase tracked shared config by accident.
