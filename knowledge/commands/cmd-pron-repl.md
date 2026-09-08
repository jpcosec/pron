---
id: cmd-pron-repl
system: pron
command_path: pron repl
synopsis: Interactive read-eval-print loop over the same Meaning layer as eval and
  the surface command.
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
provenance: src/pron/cli/main.py:_cmd_repl
---

# pron repl

## Synopsis

Interactive read-eval-print loop over the same Meaning layer as eval and the surface command.

## Purpose

Interactive read-eval-print loop over the same Meaning layer as eval and the surface command.

## How It Works

Reads a line at a time: a parenthesized line is direct Meaning, anything
else is surface tokens desugared through the anchor table, both
evaluated by the same Evaluator as `eval`. An ambiguous result opens a
pending question held in memory; typing one of its candidates on the
next line answers it in place of the ambiguous selector. `:internals`
toggles a grounding trace showing which anchor resolves each symbol;
`:help` lists the live grammar; `:quit` exits.

## Arguments

--kb <root> | optional | KB root; defaults to the current working directory.
--format json|text | optional | Output projection; defaults to text for repl (json everywhere else).

## Usage

pron repl
