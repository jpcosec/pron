# Contrato de capas: pron -> sldb

## (a) La regla y su fuente

Fuente única: el docstring del módulo `sldb/api/__init__.py` del repo sldb
(`tools/sldb/src/sldb/api/__init__.py`, líneas 1-7):

> Consumers (pron, kgdb, deskops...) call these instead of instantiating `sldb.cli` command
> classes with fake argparse namespaces. Each operation that names a store opens it the way a
> CLI command does (`open_store`), returns a pydantic model instead of printing, and raises
> `sldb.core.exceptions` errors instead of exiting. Layering: `sldb.cli` -> `sldb.api` ->
> `sldb.store` / `sldb.runtime` / `sldb.core`; nothing here imports `sldb.cli`.

Corolario para consumidores (pron): la vía pública es `sldb.api` (y el paquete
raíz `sldb` para modelos `StructuredNLDoc`). Importar de `sldb.store`, `sldb.runtime`
o `sldb.core` cruza capas: solo se admite como excepción deliberada documentada
en (c), anotada con un comentario `# Excepción deliberada: ...` in situ, y cuando
existe par en `sldb.api`, ese par se usa primero. `sldb.cli` no se importa nunca.

Verificación rápida (debe devolver solo los 23 cruces de (b); docstrings que
mencionan "sldb" no cuentan — el test (d) parsea con `ast` y los ignora):

```bash
grep -rnE '^\s*(from|import) sldb\.(store|runtime|core|cli)' --include='*.py' src/
  | grep -v 'from sldb.api'
```

## (b) Inventario de cruces que SIGUEN existiendo

23 cruces. Cada uno está anotado en el código con `# Excepción deliberada: ...`
(salvo los de `sldb.core.exceptions`, que son el contrato de errores, ver (c)).

| # | archivo:línea | import | qué es |
|---|---|---|---|
| 1 | `src/pron/docs_sync/generated_docs.py:49` | `sldb.runtime.validation` → `extract_model_data, render_model_markdown` | render/extract de markdown de modelos |
| 2 | `src/pron/docs_sync/readme_render.py:38` | `sldb.runtime.validation` → `render_model_markdown` | render de markdown de modelos |
| 3 | `src/pron/docs_sync/written_docs.py:55` | `sldb.runtime.validation` → `extract_model_data` | extract de markdown de modelos |
| 4 | `src/pron/lints.py:53` | `sldb.store.diagnostics` → `diagnose_store` | diagnosis de integridad del store |
| 5 | `src/pron/mcp/schema/model_create.py:17` | `sldb.core.exceptions` → `SLDBModelError` | tipo de error del contrato |
| 6 | `src/pron/mcp/schema/model_extend.py:16` | `sldb.core.exceptions` → `SLDBModelError` | tipo de error del contrato |
| 7 | `src/pron/sexpr/resolving/pending_match.py:22` | `sldb.store.query_engine.filter` → `DocumentFilter` | evaluador `--where` sobre payloads no salvados |
| 8 | `src/pron/sexpr/resolving/pending_match.py:23` | `sldb.store.query_engine.where_parse` → `WherePredicateError` | error del evaluador `--where` |
| 9 | `src/pron/world/storage/document_reader.py:17` | `sldb.store.io` → `load_documents_index` | lectura del índice de documentos |
| 10 | `src/pron/world/storage/document_reader.py:18` | `sldb.store.query` → `load_runtime_documents` | caché de documentos runtime |
| 11 | `src/pron/world/storage/document_tracker.py:16` | `sldb.runtime.validation` → `render_model_markdown, validate_model_data_roundtrip, validate_model_input_roundtrip` | render + validación round-trip |
| 12 | `src/pron/world/storage/linked_stores.py:14` | `sldb.core.exceptions` → `SLDBStoreError` | tipo de error del contrato |
| 13 | `src/pron/world/storage/linked_stores.py:17` | `sldb.store` → `documents_hash` | hash de documentos de un store |
| 14 | `src/pron/world/storage/linked_stores.py:18` | `sldb.store.io` → `load_store_index` | lectura del índice del store |
| 15 | `src/pron/world/storage/linked_stores.py:19` | `sldb.store.layout` → `project_root, store_exists` | paths internos del store |
| 16 | `src/pron/world/storage/linked_stores.py:20` | `sldb.store.runtime_cache` → `new_operation` | ciclo de operación (invalidación de caché) |
| 17 | `src/pron/world/storage/model_editor.py:19` | `sldb.core.exceptions` → `SLDBError` | tipo de error del contrato |
| 18 | `src/pron/world/storage/model_registry.py:20` | `sldb.core.exceptions` → `SLDBModelError` | tipo de error del contrato |
| 19 | `src/pron/world/storage/model_registry.py:23` | `sldb.store.io` → `load_documents_index, load_models_index` | lectura en bruto de índices models/documents |
| 20 | `src/pron/world/storage/payload_editor.py:13` | `sldb.core.exceptions` → `SLDBPayloadSaveError` | tipo de error del contrato |
| 21 | `src/pron/world/storage/structural_query.py:15` | `sldb.store.query` → `find_structural, get_structural, glob_structural, list_structural` | queries estructurales por address |
| 22 | `src/pron/world/storage/structural_query.py:21` | `sldb.store.query_engine.filter` → `DocumentFilter` | evaluador `--where` |
| 23 | `src/pron/world/storage/structural_query.py:22` | `sldb.store.query_engine.where_parse` → `WherePredicateError` | error del evaluador `--where` |

La lista exacta la mantiene también el test `tests/test_layer_contract.py`
(subconjunto por intersección: el test falla si aparece un cruce nuevo O si una
entrada permitida deja de existir).

## (c) Veredicto: excepción deliberada vs. evitable

Ninguno de los 23 es evitable hoy: sldb.api no expone ningún equivalente público
de lo que importan (verificado contra `__all__` de `sldb/api/__init__.py` y contra
`dir(sldb.api)`). Se clasifican en dos grupos:

- **`sldb.core.exceptions` (6 cruces: #5, #6, #12, #17, #18, #20)** — excepción
  contractual, no un accidente: el propio docstring de sldb.api declara que las
  operaciones "raises `sldb.core.exceptions` errors instead of exiting", y
  `sldb.api` **no re-exporta** las clases de error (verificado: `dir(sldb.api)`
  no contiene ninguna `*Error`). Para atrapar `SLDBModelError`, `SLDBStoreError`,
  `SLDBPayloadSaveError` y `SLDBError` no hay par público: importar la clase de
  `sldb.core.exceptions` es la única forma, y es la misma convención que usan
  deskops (`test_repo_identity.py`, `test_registry_robustness.py`) en todo el
  ecosistema. Si sldb algún día re-exporta excepciones en `sldb.api`, estas 6
  líneas se migran sin tocar comportamiento.
- **Interior funcional real (17 cruces)** — `sldb.runtime.validation`
  (render/extract/round-trip de markdown de modelos; sldb.api solo expone
  `check_edges`, `journal`, drafts y `render_document_markdown`/`render_model_template`,
  que no cubren el render de modelos), `sldb.store.*` (índices en bruto, caché
  runtime, queries estructurales por address, evaluador `--where` sobre payloads
  no salvados, paths internos, hash de documentos, `diagnose_store`,
  `new_operation`). Ninguno tiene par en sldb.api. Quedaron anotados in situ con
  `# Excepción deliberada: sldb.api no expone ...; solo lo hace <módulo>`.

### La trampa: passthroughs de `sldb.api` que NO son un arreglo

`sldb/api/__init__.py` re-exporta nombres directo desde `sldb.store` sin
implementarlos: `EdgeIndex`, `EdgeRebuildReport`, `JournalEntry`,
`JournalVerifyReport`, `EdgeNodeRecord`, `EdgeRecord` y los id builders
`anchor_node_id`, `bare`, `doc_node_id`, `field_node_id`, `kind`,
`model_node_id`, `relation_type_node_id`, `section_node_id`, `tag_node_id`.
Importarlos desde `sldb.api` es literalmente usar la superficie pública de sldb,
pero conceptualmente siguen siendo de la capa interior: el día que sldb mueva o
esconda esos tipos, pron se rompe igual que si importara de `sldb.store`.

Residuo actual (fijado por `test_no_new_api_passthrough_leaks`):

| archivo | nombres passthrough | nota |
|---|---|---|
| `src/pron/world/graph.py:15` | `EdgeIndex` | el "arreglo" de la sesión anterior fue cosmético para este nombre: solo cambió la cadena del import; el tipo sigue viniendo de `sldb.store.edge_index.edge_index`. `load_edge_index` sí es API real (`sldb.api.edges.edge_reading`). |
| `src/pron/world/graph_ids.py:7-13` | `bare`, `doc_node_id`, `field_node_id`, `kind`, `model_node_id`, `relation_type_node_id`, `tag_node_id` | pre-existente (no tocado en esta sesión): el shim re-exportador de graph_ids toma prestados los id builders de `sldb.store.edge_index.node_ids` vía la superficie de sldb.api. |

No se "arregla" ahora (requeriría o bien mover los tipos en sldb — otro repo,
prohibido — o envolverlos en pron con un shim propio que los re-implemente,
fuera del alcance de esta auditoría). Quedan como deuda de superficie, explícita
y vigilada por el test.

### Lo que se arregló (14 imports de interior -> sldb.api, más los 2 peores)

La sesión anterior movió 14 imports de `sldb.store` (interior) a `sldb.api`, y
arregló los 2 peores (`lints.py`, `pending_match.py`), que cruzaban directo al
interior para funcionar. Qué estaba mal y cómo quedó:

| archivo | antes (mal) | después (bien) |
|---|---|---|
| `world/graph.py` | `from sldb.store.edge_index.edge_index import EdgeIndex` (interior; evitable) | `load_edge_index` desde `sldb.api` (API real). Ojo: `EdgeIndex` también se movió a `sldb.api`, pero es cosmético — es passthrough directo del mismo módulo interior, ver sección de la trampa. |
| `world/storage/document_reader.py` | `from sldb.store.io import load_documents_index` sin par público a la vista | `resolve_model_ref` desde `sldb.api`; `sldb.store` queda solo con lo que no tiene par, anotado |
| `world/storage/document_tracker.py` | `track_document_file, untrack_document` desde interior | desde `sldb.api` |
| `world/storage/linked_stores.py` | `link_store, open_store, update_store_indexes, StoreUpdateReport` desde interior | desde `sldb.api` |
| `world/storage/model_registry.py` | `load_registered_model` etc. desde interior | desde `sldb.api` |
| `world/storage/structural_query.py` | `resolve_model_ref` desde interior | desde `sldb.api` |
| `docs_sync/generated_docs.py`, `readme_render.py`, `written_docs.py` | imports de interior sin par público a la vista | `resolve_model_ref`/pares desde `sldb.api` cuando aplica; interior solo anotado |
| `lints.py` (2 peor) | `diagnose_store` directo al interior | `resolve_model_ref` desde `sldb.api`; `diagnose_store` anotado como excepción (no hay `diagnose_store` en sldb.api; solo `check_edges`/`journal`, que no cubren la diagnosis de integridad completa) |
| `sexpr/resolving/pending_match.py` (2 peor) | `DocumentFilter`/`WherePredicateError` directo al interior | `resolve_model_ref` desde `sldb.api`; el evaluador `--where` sobre payloads no salvados anotado (solo existe en `query_engine`, no en sldb.api) |

Regla usada para decidir: primero se usa el par de `sldb.api` si existe; el cruce
restante se conserva y se anota solo cuando sldb.api no tiene equivalente alguno.
El comentario de `linked_stores.py:17` deja constancia del precedente del
ecosistema: `graph_ui/frontends/mindmap/sldb_adapter.py` usa el mismo criterio.

## (d) Enforcer: `tests/test_layer_contract.py`

Recorre `src/pron/**/*.py`, parsea con `ast` y falla si un módulo fuera de la
lista permitida importa una capa interior (`sldb.store`, `sldb.runtime`,
`sldb.core`, `sldb.cli`), o si importa un nombre nuevo de una capa interior ya
permitida, o si una entrada permitida deja de existir (evita reglas muertas).

Además, `test_no_new_api_passthrough_leaks` fija la lista de passthroughs de
`sldb.api` (nombres que sldb re-exporta directo desde `sldb.store` sin
implementar) y falla si alguien toma prestado uno nuevo desde `sldb.api` para
"arreglar" un cruce moviendo la cadena del import: ese movimiento no es un
arreglo, es cosmetizar la fuga (ver (c), sección de la trampa).

Procedimiento para un cruce nuevo legítimo: añadir el import con su comentario
`# Excepción deliberada: ...` in situ, agregar la entrada a `ALLOWED` en el test,
y documentarlo en (b)/(c) de este archivo. Sin esos tres pasos el test es rojo.

```bash
pytest tests/test_layer_contract.py    # rojo si hay un cruce no documentado
```

Fuera del alcance de este test (por diseño): `sldb.api` (capa pública, permitida),
el raíz `sldb` (`from sldb import StructuredNLDoc`, modelos, público), y los
`tests/` de pron.