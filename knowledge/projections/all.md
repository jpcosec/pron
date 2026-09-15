---
name: all
stores:
- local
models:
- SpecDoc
- CliCommandDoc
- SurfaceDoc
- AnchorDoc
- ProjectionDoc
- MoveDoc
- ExplanationDoc
- ReadmeDoc
relations:
- name: implements
  mode: read
actions:
- refresh
aliases:
- all
naming: {}
display:
  SpecDoc: '{title}'
  CliCommandDoc: pron {command_path}
  SurfaceDoc: '{surface}'
  MoveDoc: '{id}: {sentence}'
  ExplanationDoc: '{answer}'
  ReadmeDoc: '{title}'
key: {}
matching:
  neighbors: 3
  threshold: 0.55
---

# all

pron's own knowledge base: read it, ask it; it is regenerated from the repo, so it is not written by hand.
