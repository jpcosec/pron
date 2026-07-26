# spec2viz Views

Derived diagram specs and rendered outputs for the `knowledge` repo.

## Layout

- `specs/` contains semantic YAML inputs for `spec2viz`
- `out/default/` contains default renderer outputs
- `out/mermaid/` contains Mermaid outputs for compatible diagram types

## Refresh

From the repo root:

```bash
spec2viz validate views/spec2viz/specs/*.yml
spec2viz render views/spec2viz/specs/*.yml --out views/spec2viz/out/default
spec2viz render views/spec2viz/specs/component.kb-canonical-layers.yml views/spec2viz/specs/component.source-app-synthesis.yml views/spec2viz/specs/sequence.author-source-sample-atom.yml views/spec2viz/specs/sequence.retrieval-pipeline.yml views/spec2viz/specs/state.grounding-maturity.yml views/spec2viz/specs/state.proposition-lifecycle.yml views/spec2viz/specs/activity.bootstrap-path.yml views/spec2viz/specs/activity.retrieval-workflow.yml views/spec2viz/specs/deployment.operator-surfaces.yml --backend mermaid --out views/spec2viz/out/mermaid
```
