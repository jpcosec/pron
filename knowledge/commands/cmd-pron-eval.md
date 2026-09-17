---
id: cmd-pron-eval
system: pron
command_path: eval
synopsis: Evaluate one move written as forms (spec 13) and print the answer, with
  the trace on request.
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:cli_command
provenance: src/pron/cli/commands/eval.py:command
---

# eval

## Synopsis

Evaluate one move written as forms (spec 13) and print the answer, with the trace on request.

## Purpose

Evaluate one move written as forms (spec 13) and print the answer, with the trace on request.

## How It Works

The same move a sentence resolves to, without the natural language surface: nouns by
address (doc "Model:name") or by predicate (find Model (where "...")), and the kernel's
verbs, relations and aliases by name. Goes through the running `pron serve` when one listens.

## Arguments

--world | optional | World root (contains .sldb)
--pythonpath | optional | Project path where the world's models import from
forms | required | 
--projection | optional | 
--speaker | optional | 
--now | optional | 
--trace | optional | 
--local | optional | Open the world here even if a server listens
--socket | optional | The daemon's socket, when the world's .pron/serve.sock is not it
--home | optional | The caller's own world (name or path); another world opens only its exposed projections

## Usage

pron eval '(say confirm (doc "Reservation:reservation-x"))' --world . [--projection all] [--speaker me] [--trace] [--local]
