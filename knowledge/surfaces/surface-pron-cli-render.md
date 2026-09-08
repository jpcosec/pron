---
id: surface-pron-cli-render
system: pron
surface: pron.cli.render
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
provenance: src/pron/cli/render.py
---

# pron.cli.render

## Purpose

Renderer: result values -> JSON (default) or text, always with refs

## How It Works

atom-every-read-response-carries-refs-for-auditability: Every read result includes the refs (document paths and graph node ids) that produced it, so any answer can be audited back to the exact tracked documents and edges. JSON is the default output for agents and pipes; text is a projection.

atom-semantic-errors-answer-symbol-motive-and-next-action: Every semantic error states three things: which symbol failed, what motive it has (or that it has none), and what the user can do next (nearest candidates for missing nouns, anchor-declaration hint for unknown operations). Never a stacktrace, never a bare 'unknown flag'.

## Commands

render(value: object, fmt: str='json') -> tuple[str, int] | Render any result value; returns (text, exit_code).
