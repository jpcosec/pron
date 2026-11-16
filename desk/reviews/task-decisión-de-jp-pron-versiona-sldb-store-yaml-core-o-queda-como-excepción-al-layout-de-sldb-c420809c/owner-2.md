---
sldb:
  by: agent
  at: '2026-11-16T05:13:26Z'
  authority: generated
  via: save_document_payload
# review-<task>-<kind>-<n>
id: review-task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c-owner-2
# preflight | bundle | reproduction | goldens | owner | node | evidence
kind: owner
# kind evidence only: tests | commit | atom | materialization | document | external
fact: ''
# kind evidence only: what the producer verified, one item per line
value: ''
# doc:<Model>:<id> or empty for reviews of plan nodes
subject: doc:TaskDecisionDoc:task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c@sha256:217624b4472d6e0c4a300f24e0ccec4afe5cdfacda4acf49c116931a8765cd03
# <plan>/dag.yaml#node:<ID>; empty when subject names a document
subject_ref: ''
# RuntimeProfileDoc name or "human"
engine: human
actor: pron-repair
# Run evidence directory under runs/, relative to the project root
run_dir: ''
input_sha256: ''
output_sha256: ''
# pending | accepted | rejected | incomplete
verdict: accepted
reason: 'Opción A: JP 2026-11-16 (transmitida por el supervisor). Se versionan .sldb/store.yaml
  y .sldb/core/; no se versiona la parte runtime/caché del store (.sldb_cache/ y lo
  que sea runtime), que sigue ignorada.'
# ISO 8601 timestamp
created_at: '2026-11-16T04:13:30.181084+00:00'
# ISO 8601 timestamp, empty while pending
disposed_at: '2026-11-16T05:13:21.911717+00:00'
disposed_by: pron-repair
# e.g. workspace:desk
tags:
- workspace:desk
---

# Owner review of task-decisión-de-jp-pron-versiona-sldb-store-yaml-core-o-queda-como-excepción-al-layout-de-sldb-c420809c

## Summary

_Summarize what was reviewed and the evidence this receipt records._

owner receipt recorded by pron-repair; evidence: (none)

## Disposition

_Record the verdict rationale and who disposed of the review._

Verdict accepted: Opción A: JP 2026-11-16 (transmitida por el supervisor). Se versionan .sldb/store.yaml y .sldb/core/; no se versiona la parte runtime/caché del store (.sldb_cache/ y lo que sea runtime), que sigue ignorada.
