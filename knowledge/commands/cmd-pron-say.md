---
id: cmd-pron-say
system: pron
command_path: say
synopsis: Say one sentence to a world and print the answer, with the trace on request.
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:cli_command
provenance: src/pron/cli/main.py:_cmd_say
---

# say

## Synopsis

Say one sentence to a world and print the answer, with the trace on request.

## Purpose

Say one sentence to a world and print the answer, with the trace on request.

## How It Works

Opens a session with the projection and speaker given, runs one turn, prints the
answer in natural language; --trace adds the addresses, edges and writes.

## Arguments

--world | optional | World root (contains .sldb)
--pythonpath | optional | Project path where the world's models import from
sentence | required | 
--projection | optional | 
--speaker | optional | 
--now | optional | 
--trace | optional | 

## Usage

pron say "what tables are on the terrace?" --world . [--projection all] [--speaker me] [--trace]
