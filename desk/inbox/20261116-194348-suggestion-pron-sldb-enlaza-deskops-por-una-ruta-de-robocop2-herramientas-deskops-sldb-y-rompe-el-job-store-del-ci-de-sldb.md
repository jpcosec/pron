---
sldb:
  by: agent
  at: '2026-11-17T01:39:17Z'
  authority: generated
  via: save_document_payload
# unclear | suggestion
kind: suggestion
# e.g., other_repo
sender_project: sldb
# e.g., target_repo
target_project: pron-repair
# ISO 8601 timestamp
created_at: '2026-11-16T19:43:48'
# open | closed
status: closed
# project identity that acknowledged the note
acknowledged_by: pron-repair
# ISO 8601 timestamp, set when acknowledged
acknowledged_at: '2026-11-16T22:39:05'
---

# pron/.sldb enlaza deskops por una ruta de robocop2 (../../../herramientas/deskops/.sldb) y rompe el job store del CI de sldb

_Describe the incoming message with enough evidence to triage._

En pron/.sldb/store.yaml, el enlace deskops es 'path: ../../../herramientas/deskops/.sldb', que solo resuelve en robocop2. En el CI de sldb (pron en $GITHUB_WORKSPACE/pron y deskops en $GITHUB_WORKSPACE/deskops), 'pron docs' falla con 'No store_index.yaml at .../herramientas/deskops/.sldb' y el job store queda en rojo. Propuesta: enlazar el repo hermano '../../deskops/.sldb' (existe en robocop2 en /mnt/ssd/proyectos/SLDB_1/deskops y en el runner) con el CLI de sldb, y verificar 'make world' y 'pron docs' en rc 0 en un clon limpio. Contexto: sldb ya arregla el otro fallo del mismo job (re-track con force, init --world).
