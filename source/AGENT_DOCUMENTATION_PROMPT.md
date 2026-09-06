# Prompt: Document-as-you-build (knowledge rigor)

You are developing software inside the `hum-ecosystem` / `legos` workspace. Every
unit of work you produce MUST be documented as durable knowledge with the same
rigor described below. Documentation is not a final step; it is part of the
definition of done for each change.

## Non-negotiable rules

1. Knowledge lives as atoms. One atom = one stable claim answering exactly one
   5WH1+ question (`what | why | how | how_not | when | where | for_whom`).
2. Every atom is a tracked SLDB document using the `AtomDoc` model. Do not write
   free-form Markdown notes as a substitute for atoms.
3. Every atom carries mandatory namespaced tags, exactly one of each:
   - `domain:<field>` — one of: provenance, knowledge_representation,
     graph_architecture, retrieval, source_modeling, governance,
     system_architecture, code_craft.
   - `kind:<software|concept>` — software = a runnable/implementable artifact;
     concept = a theory/model/principle.
   - `impl:<here|external|pending>` — here = implemented in this repo; external =
     implemented in another repo/tool; pending = not implemented yet.
4. `code_craft` atoms additionally carry `practice:` and `lang:` facets.
5. `provenance:` must point to the authoritative source (code path, spec section,
   or file+locator). No fake retroactive provenance. If nothing is grounded yet,
   say so explicitly; do not invent samples.
6. Tags are facets, not hierarchy. Do not encode taxonomy in folders. Do not use
   tags as a substitute for explicit relations.
7. Namespaces are closed. Only use namespaces defined in
   `knowledge/atoms/tag-namespaces.yaml`, each with a `do_not_use_when` boundary.
   If you need a new namespace or value, propose it there first.

## What you MUST document for every feature/command you build

For each CLI command or public surface you create, produce a self-describing
document (models `CliCommandDoc` / `SurfaceDoc` in
`sldb.models.knowledge_surface`) so that `--help` can be populated from the
document and vice versa. Capture, at minimum:

- **purpose** — why it exists, the problem it solves.
- **how it works** — step by step, and how it uses the store/graph/runtime.
- **synopsis** — the one-line help string (= argparse `help=`).
- **arguments** — one per line as `<name> | required|optional | <help>`,
  mirroring the real parser.
- **usage** — a concrete, runnable example.
- **provenance** — the code path that implements it.

For each durable concept or design decision, produce an `AtomDoc` covering the
relevant 5WH1+ angle(s): what it is, why it matters, how it works, when it
applies, and (if code) where it lives.

## Workflow (do this, in order)

1. Before coding: draft the atoms for the design decisions you are about to make
   (`impl:pending`). This forces the design to be legible.
2. Build the code.
3. After coding: create/update the command & surface docs from the REAL argparse
   tree (extract programmatically, do not hand-wave). Flip `impl:pending` →
   `impl:here` for what you actually implemented.
4. Track every new doc in the SLDB store and rebuild indexes:
   ```bash
   python -m sldb docs track <path> --model <Model> --store .sldb --pythonpath .
   python -m sldb stores update --store .sldb --pythonpath .
   python -m sldb stores check --store .sldb   # must print PASS
   ```
5. Validate the roundtrip: `sldb extract <model> <doc.md> <out.yaml>` must
   reproduce the payload. A command doc whose fields do not roundtrip is a bug.
6. Commit code + docs together. A commit that changes behavior without updating
   its atoms/command docs is incomplete.

## Acceptance criteria (self-check before you say "done")

- [ ] Every new command has a `CliCommandDoc`; every new surface a `SurfaceDoc`.
- [ ] Every durable decision has an `AtomDoc` with the correct single 5WH1+.
- [ ] Every atom has exactly one `domain:`, one `kind:`, one `impl:`.
- [ ] All tags are within the allowlist in `tag-namespaces.yaml`.
- [ ] `provenance` points to real code/spec; no invented evidence.
- [ ] `sldb stores check` prints `PASS: store integrity`.
- [ ] Command docs roundtrip cleanly (extract == payload).
- [ ] The goal is met: someone can "read the code" through the atoms without
      opening the source first.

## The north star

Each app that uses `knowledge` should become a self-aware knowledge entity over
sldb+kgdb: its CLI, surfaces, and design are queryable knowledge, its `--help` is
derivable from documents, and its behavior is traceable to durable atoms. Build
so that the knowledge layer stays true to the code, not drifting from it.
