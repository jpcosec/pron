---
id: cmd-pron-eval
system: pron
command_path: pron eval
synopsis: Evaluate an s-expression directly against the Meaning layer.
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
provenance: src/pron/cli/main.py:_cmd_eval
---

# pron eval

## Synopsis

Evaluate an s-expression directly against the Meaning layer.

## Purpose

Evaluate an s-expression directly against the Meaning layer.

## How It Works

Parses the expression, resolves nouns and anchors through
AnchorRegistry, and evaluates it with Evaluator against SLDB and KGDB.
Ambiguous resolutions are persisted as a pending clarification in
.pron/session.json.

## Arguments

<s-expr> | required | The s-expression to evaluate, e.g. '(check (doc atom "x") :project title)'.
--kb <root> | optional | KB root; defaults to the current working directory.
--format json|text | optional | Output projection; defaults to json.

## Usage

pron eval '(check (doc atom "atom-x") :project title)'
