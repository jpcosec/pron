---
sldb:
  by: agent
  at: '2026-11-17T01:39:40Z'
  authority: generated
  via: save_document_payload
# unclear | suggestion
kind: suggestion
# e.g., other_repo
sender_project: sldb
# e.g., target_repo
target_project: pron-repair
# ISO 8601 timestamp
created_at: '2026-11-16T19:57:24'
# open | closed
status: closed
# project identity that acknowledged the note
acknowledged_by: pron-repair
# ISO 8601 timestamp, set when acknowledged
acknowledged_at: '2026-11-16T22:39:29'
---

# sldb: track con force re-indexa; make world vuelve a pasar, pero el enlace a deskops no resuelve en CI

_Describe the incoming message with enough evidence to triage._

sldb: docs track --force (y track_document_file con force=True) re-indexa desde el archivo un documento ya trackeado en la misma ruta, en lugar de fallar con 'already tracked'. Commits f3d51b29 (código) y 8eb9aa9c (closeout); wA:p1 los integra y avisa del push. Repetirlo sin cambios es idempotente. Con force y otra ruta falla nombrando las dos (para mover está move). Sin force el error no cambia. Con esto make world de pron master 39ea972 da rc 0 contra sldb (antes fallaba con rt-implements already tracked). Queda un problema de pron: .sldb/store.yaml enlaza deskops como path: ../../../herramientas/deskops/.sldb, que solo resuelve en el layout de robocop2. En el runner del CI de sldb (pron y deskops lado a lado en GITHUB_WORKSPACE) pron docs falla con No store_index.yaml at .../herramientas/deskops/.sldb. Lo deriva el integrador de sldb (wA:p1).
