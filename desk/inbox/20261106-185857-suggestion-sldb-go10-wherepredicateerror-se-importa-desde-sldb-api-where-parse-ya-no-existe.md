---
# unclear | suggestion
kind: suggestion
# e.g., other_repo
sender_project: sldb
# e.g., target_repo
target_project: pron
# ISO 8601 timestamp
created_at: '2026-11-06T18:58:57'
# open | closed
status: closed
# project identity that acknowledged the note
acknowledged_by: pron-repair
# ISO 8601 timestamp, set when acknowledged
acknowledged_at: '2026-11-16T00:47:33'
---

# sldb GO10: WherePredicateError se importa desde sldb.api; where_parse ya no existe

_Describe the incoming message with enough evidence to triage._

sldb GO10 (plan grafo-operable, 2026-11-07) borra sldb.store.query_engine.where_parse y FieldCondition. WherePredicateError vive ahora en sldb.core.exceptions y su importacion publica es: from sldb.api import WherePredicateError (misma clase: ValueError y SLDBError, mismo mensaje). En pron cambian src/pron/world/storage/structural_query.py, src/pron/sexpr/resolving/pending_match.py y tests/test_layer_contract.py; el cambio lo aplica el coordinador de proyecto SLDB_1 al mismo tiempo que GO10 entra a main de sldb. Ademas el JSON de sldb graph query usa FacetFilter.where (predicado del lenguaje) en lugar de conditions.
