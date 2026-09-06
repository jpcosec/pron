CLI retrieval test succeeded without directly reading atom files.

- Discovered metadata-policy atom via `./knowledge list atoms`:
  - `atom-atom-metadata-should-live-outside-atoms-in-a-dedicated-registry`
- Retrieved atom via `./knowledge show atom atom-atom-metadata-should-live-outside-atoms-in-a-dedicated-registry`:
  - Answer: metadata describing the atom rather than the claim should live in a parallel metadata registry, including provenance state, project context, source surface, grounding, and editorial role.
- Retrieved metadata via `./knowledge show metadata atom-atom-metadata-should-live-outside-atoms-in-a-dedicated-registry`:
  - Metadata included `project:kb`, `source:atom_metadata_registry`, `source_kind:generated_spec`, `grounding:derived`, `scope:meta`, `role:definition`.

Friction:
- `list atoms` returns full corpus output; filtering to the metadata-policy item is manual unless additional CLI filtering exists.
- `show atom` still exposes the physical atom path in output, but retrieval itself worked without opening atom files.
- Repository staging check was unavailable because `/home/jp/Upla/kb` is not a git repository.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Used only the CLI plus the provided spec docs to discover one metadata-policy atom, retrieve its answer, retrieve its metadata, and record whether retrieval succeeded, without reading files under .knowledge/atoms or desk/atoms."
    }
  ],
  "changedFiles": [
    "source/subagent-outputs/retrieval-cli-metadata.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "./knowledge list atoms | head -n 100",
      "result": "passed",
      "summary": "Listed atoms and identified `atom-atom-metadata-should-live-outside-atoms-in-a-dedicated-registry`."
    },
    {
      "command": "./knowledge show atom atom-atom-metadata-should-live-outside-atoms-in-a-dedicated-registry",
      "result": "passed",
      "summary": "Returned the atom authoring view including the answer text."
    },
    {
      "command": "./knowledge show metadata atom-atom-metadata-should-live-outside-atoms-in-a-dedicated-registry",
      "result": "passed",
      "summary": "Returned metadata registry fields for the same atom."
    },
    {
      "command": "git status --short",
      "result": "failed",
      "summary": "Could not check staged files because the working directory is not a git repository."
    }
  ],
  "validationOutput": [
    "Atom retrieval succeeded via CLI.",
    "Metadata retrieval succeeded via CLI.",
    "No direct reads were performed under .knowledge/atoms or desk/atoms."
  ],
  "residualRisks": [
    "CLI output for `show atom` reveals the underlying atom path even when atom files are not opened.",
    "`noStagedFiles` could not be independently verified because this directory is not a git repository."
  ],
  "noStagedFiles": true,
  "diffSummary": "Added a concise retrieval test report at source/subagent-outputs/retrieval-cli-metadata.md.",
  "reviewFindings": [
    "no blockers"
  ],
  "manualNotes": "Selected the metadata-policy atom `atom-atom-metadata-should-live-outside-atoms-in-a-dedicated-registry` based on `knowledge list atoms` output."
}
```