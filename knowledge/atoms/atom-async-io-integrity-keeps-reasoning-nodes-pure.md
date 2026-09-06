---
id: atom-async-io-integrity-keeps-reasoning-nodes-pure
title: Async I/O integrity keeps reasoning nodes pure
five_wh_one_plus: how
tags:
- domain:code_craft
- kind:concept
- impl:pending
- practice:runtime_integrity
- lang:python
- system:hum_scrapper
provenance: Extracted and synthesized from clean-code/quality atoms across humble, deskops, sldb-refactor, hum-scrapper, Cotizador, and marcado repos.
---

# Async I/O integrity keeps reasoning nodes pure

## Answer

Live I/O should stay at adapter and persistence boundaries: domain objects expose explicit load and save methods and graph state stays a pure data structure, so no blocking, hidden, or node-local physical I/O happens inside reasoning or routing nodes, keeping each turn auditable and deterministic.
