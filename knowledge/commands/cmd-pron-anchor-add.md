---
id: cmd-pron-anchor-add
system: pron
command_path: pron anchor add
synopsis: 'Declare a new grammar symbol: writes an AnchorDoc and tracks it.'
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
provenance: src/pron/cli/main.py:_cmd_anchor_add
---

# pron anchor add

## Synopsis

Declare a new grammar symbol: writes an AnchorDoc and tracks it.

## Purpose

Declare a new grammar symbol: writes an AnchorDoc and tracks it.

## How It Works

Validates symbol, kind, ref and motive, writes the AnchorDoc through the
sldb bridge, tracks it and refreshes the store so the symbol resolves on
the next call.

## Arguments

<symbol> | required | The grammar symbol being declared.
--kind model|expr|operation | required | The anchor's kind.
--ref <typed-ref> | required | The referent, e.g. model:AtomDoc or 'expr:(related (doc atom _))'.
--motive <text> | required | The semantic motive for the symbol.
--kb <root> | optional | KB root; defaults to the current working directory.
--format json|text | optional | Output projection; defaults to json.

## Usage

pron anchor add tagged --kind expr --ref "expr:(rel tagged _)" --motive "..."
