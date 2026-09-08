---
id: cmd-pron-anchors
system: pron
command_path: pron anchors
synopsis: 'List the live grammar: anchors bound to models, expressions and operations.'
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
provenance: src/pron/cli/main.py:_cmd_anchors
---

# pron anchors

## Synopsis

List the live grammar: anchors bound to models, expressions and operations.

## Purpose

List the live grammar: anchors bound to models, expressions and operations.

## How It Works

Reads AnchorDoc documents tracked in the store through AnchorRegistry and
renders each symbol's kind, ref and motive. With a symbol argument,
resolves and renders that one anchor.

## Arguments

[symbol] | optional | Filter to a single anchor symbol.
--kb <root> | optional | KB root; defaults to the current working directory.
--format json|text | optional | Output projection; defaults to json.

## Usage

pron anchors
pron anchors atom --format text
