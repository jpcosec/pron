---
id: cmd-pron-repl
system: pron
command_path: repl
synopsis: Talk to a world, one sentence per line.
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:cli_command
provenance: src/pron/cli/main.py:_cmd_repl
---

# repl

## Synopsis

Talk to a world, one sentence per line.

## Purpose

Talk to a world, one sentence per line.

## How It Works

The same session as `say`, kept open: pending questions and referents survive between
lines. `:trace` toggles the trace, `:lexicon [MODEL]` lists words, `:quit` leaves.

## Arguments

--world | optional | World root (contains .sldb)
--pythonpath | optional | Project path where the world's models import from
--projection | optional | 
--speaker | optional | 
--now | optional | 

## Usage

pron repl --world . [--projection all] [--speaker me]
