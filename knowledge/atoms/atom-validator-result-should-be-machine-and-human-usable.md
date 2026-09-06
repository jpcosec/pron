---
id: atom-validator-result-should-be-machine-and-human-usable
title: Validator result should be machine- and human-usable
five_wh_one_plus: how
tags:
- domain:code_craft
- kind:concept
- impl:pending
- practice:linting_mechanical
- lang:generic
- system:marcado
provenance: Extracted and synthesized from clean-code/quality atoms across humble, deskops, sldb-refactor, hum-scrapper, Cotizador, and marcado repos.
---

# Validator result should be machine- and human-usable

## Answer

A validator result should carry global status, a list of findings with severity, affected namespace, locator/provenance, the violated rule, and a correction hint when possible, so the same finding is stable across Mermaid, CLI, JSON, or UI renderers and is never an unlocatable bare "invalid".
