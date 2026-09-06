# Retrieval CLI graph test

I tested retrieval without directly opening atom files.

## Result
- Retrieval **succeeded** via CLI.
- Discovery worked with `./knowledge list atoms`.
- Retrieval worked with `./knowledge show atom <selector>`.

## Atom used
- Selector: `atom-graph-trace-should-answer-provenance-lineage-across-the-source-sample-atom-composition-chain`

## Retrieved answer
> `knowledge graph trace` should operationalize provenance lineage by walking the chain from Source to Sample to Atom to Composition and back as needed. In this KB, trace is the command that should make source-grounded support recoverable to a human, not just prove that a node exists.

## Useful extra check
- `./knowledge graph list --type atom | head -n 10` worked and returned atom graph nodes.

## Friction
- The CLI is successful for retrieval, but the `knowledge` script clearly resolves atoms from `.knowledge/atoms` or `desk/atoms` on disk, so this does **not** demonstrate storage independence from physical atom files.
- `show atom` exposes the backing file path (`.knowledge/atoms/...md`), which reinforces that the current retrieval path is still file-backed.
- `./knowledge list atoms | head` ends with a harmless broken-pipe message because `head` closes stdout early.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Completed the requested CLI-only retrieval check, avoided reading .knowledge/atoms and desk/atoms directly, and wrote findings to the required output path."
    }
  ],
  "changedFiles": [
    "/home/jp/Upla/kb/subagent-outputs/retrieval-cli-graph.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "cd /home/jp/Upla/kb && ./knowledge list atoms | head -n 40",
      "result": "passed",
      "summary": "Listed atoms and found graph/provenance-related candidates, including the graph trace atom."
    },
    {
      "command": "cd /home/jp/Upla/kb && ./knowledge show atom atom-graph-trace-should-answer-provenance-lineage-across-the-source-sample-atom-composition-chain",
      "result": "passed",
      "summary": "Retrieved the atom answer successfully via CLI."
    },
    {
      "command": "cd /home/jp/Upla/kb && ./knowledge graph list --type atom | head -n 10",
      "result": "passed",
      "summary": "Confirmed graph snapshot listing works for atom nodes."
    },
    {
      "command": "cd /home/jp/Upla/kb && git status --short",
      "result": "passed",
      "summary": "Repository has no .git directory here, so there are no staged files in this working tree."
    }
  ],
  "validationOutput": [
    "CLI retrieval succeeded for a provenance/trace atom.",
    "Graph node listing also succeeded.",
    "git status reported 'not a git repository', so staged-file state is effectively not applicable here."
  ],
  "residualRisks": [
    "The current knowledge CLI is still file-backed and resolves atoms from .knowledge/atoms or desk/atoms, so this test does not prove retrieval independence from physical atom storage."
  ],
  "noStagedFiles": true,
  "diffSummary": "Added the requested findings report only.",
  "reviewFindings": [
    "no blockers"
  ],
  "manualNotes": "I did not directly read any files under .knowledge/atoms or desk/atoms; retrieval used the CLI only."
}
```