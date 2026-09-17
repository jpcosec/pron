# Roadmap a sldb v2 — desde pron

Estado al 2026-09-17. Qué hay que hacer, en qué orden, y **en qué repo**, para llegar a
sldb v2 — sabiendo que hoy hay dos caminos abiertos hacia él y que sólo uno tiene manos
encima.

Documentos de referencia: `~/proyectos/kimun/docs/v2/` (`05-estado.md` es el punto de
entrada, `08-distribucion.md §0-§1` la topología de repos). Este documento cubre lo que
esos no cubren: **el lado de acá**, que `08 §1` deja explícitamente fuera de plan
(*"pron no se toca desde aquí durante S0–S6"*).

## 0. El estado real

### 0.1 Las tres capas de un mundo de pron

Las tres derivan del store de sldb; ninguna tiene identidad propia.

| capa | dónde vive | quién la escribe | frescura |
|---|---|---|---|
| documentos (fuente de verdad) | `.sldb/` + los markdown (`knowledge/`, `ledger/`, `source/spec/`, `kgdb/relation_types/`) | sldb, por `pron.world.store.Store` | `hash_a` store, `hash_b` modelo, `hash_c` documento |
| grafo tipado | `.pron/graph.nx.json` | `GraphRefresher` → `kgdb.ingest.typed.build_typed_snapshot` | `hash_b` por modelo, **solo store local** |
| índice del corpus | `.pron/docs[.<text>].<embedder>.json` | `Corpus.refresh()` → `DocumentIndex` | `hash_c` por documento, **federado** |

### 0.2 Código como documento: ya funciona

| pieza | dónde | qué hace | vivo |
|---|---|---|---|
| `PythonScanner` | `sldb/selfdoc/python_scanner.py` | `ast.parse`, sin importar ni ejecutar; emite `PythonSymbol` (pydantic) | sí |
| `PythonSymbolDoc` | `sldb/models/python_symbol_doc.py` | el contrato: `module`, `qualname`, `kind`, `source_span`, `source_sha256`, `signature`, `docstring`, `imports`, más campos autorados (`purpose`, `architecture`) | sí |
| `plan_python_documents` | `sldb/selfdoc/python_materialize.py` | proyecta los símbolos a markdown y los trackea | sí |
| `source_snapshot` + `kgdb_sync` | `sldb/selfdoc/python_source_graph.py`, `kgdb_sync.py` | arma aristas `contains`/`imports`/`references` y las mete a kgdb **por `subprocess`** | sí |
| `python_relation_registry` | `sldb/selfdoc/python_relation_registry.py` | valida esas aristas contra los `RelationTypeDoc` registrados | sí |
| `TypeScriptScanner` | `sldb/core/ingest/typescript_scanner.py` | — | **no**: importa `ontology` y `wiki_compiler`, que no existen en el entorno |

### 0.3 Dónde están las manos (2026-09-17)

| repo | último commit | estado |
|---|---|---|
| **kimun** (sldb v2) | **2026-09-07**, hace diez días | `2.0.0-alpha.1`. Kernel 0–6 cerrado, pista S en **S0**; S1 figura como "siguiente" y no empezó. El board activo tiene **cero** tasks de la pista S: son las siete de deuda del kernel (oráculo, contención, ULID, GC, paridad Node, spec2viz, tooling) |
| **sldb v1** | 2026-09-17 | **25 commits después del tag `v1-frozen`** |
| **kgdb** | 2026-09-17 | merkle incremental, `__references__` |
| **pron** | 2026-09-17 | 51 commits hoy; 24 el 15; 12 el 14 |

## 1. El hallazgo: v1 ya está caminando el roadmap de v2

El congelamiento de v1 (`kimun/docs/v2/05 §3`, decisión 12; tags `v1-frozen`) es letra
muerta, y lo que pasó en esos 25 commits no es mantenimiento: es la arquitectura de v2,
implementada en Python, sin haberlo escrito.

| lo que pasó en v1 | a qué converge en kimun |
|---|---|
| merkle capas 5–8: `semantic`, `sections` y `documents index` como shards **por documento**; escritura por camino; tras una escritura ningún consumidor recorre cada hoja | árboles con Merkle perezoso, escritura como transacción que toca su propio camino — kernel hito 3 |
| `sldb.api`: paquete tipado como librería; la CLI lo usa y reexporta lo movido; kgdb deja de importar `sldb.cli` | los anillos 0/1/2 (`sldb.kernel` / `sldb.host` / `sldb.surface`; ring 2 puede requerir el kernel, nunca al revés) — `06 §2` |
| `selfdoc`: AST de Python → `PythonSymbolDoc` trackeado | "los documentos Markdown son proyecciones del pool" — la tesis del producto |
| `AnchorDoc kind=expr`: plantillas s-expression con huecos para relaciones derivadas | los anchors de pron como gramática por defecto — S7, `08 §1` A4 |
| hash en cadena `hash_a`/`hash_b`/`hash_c`/`hash_d` con caches invalidadas por la cadena | ids content-addressed y estados de anclaje derivados — kernel 1–4 |

Dicho de otro modo: **la distancia entre v1 y v2 se está cerrando desde el lado de v1**,
y a un ritmo mucho mayor que desde el lado de kimun, que no se mueve hace diez días.

## 2. La decisión de fondo

Hay dos caminos a sldb v2, y hoy están los dos abiertos:

| | **A — kimun absorbe** | **B — v1 se convierte** |
|---|---|---|
| qué es v2 | el kernel Clojure/bb content-addressed que ya existe en kimun | aquello en lo que sldb v1 termina, capa por capa, en Python |
| el cruce | `kimun migrate --from-v1` (S2) sobre una copia; pron porta su evaluador (S4, S7) | no hay cruce: hay una v2 declarada cuando el sustrato ya cambió |
| qué falta | S1–S7 completos: modelos, docs/fields/sections, índices, evaluador, derivados, cliente Python, gramática | nodos content-addressed en vez de archivos+paths; anclaje en vez de guarda por `hash_c`; aristas como índice del store |
| lo ya construido | kernel 0–6: pool S/M/G, árboles de posiciones, aristas con evidencia, `TransactionPlan`, estados de anclaje, reconciliación, stand-off UAX #29 | 25 commits de convergencia real, `sldb.api`, merkle 5–8, selfdoc, pron sobre 201 tests |
| riesgo | que S1–S7 nunca arranquen y el trabajo real siga pasando en v1 por diez días más, después veinte | perder el kernel de kimun, que es bueno y está probado (150 tests, oráculo de bytes canónicos independiente) |

Este documento **no decide** entre A y B: es del usuario. Lo que sí hace es ordenar el
trabajo de manera que las primeras fases valgan igual en los dos escenarios, y dejar la
decisión para cuando sea inevitable — que es al empezar la Fase 3.

## 3. Fase 1 — una sola puerta (repo: **pron**) · vale en A y en B

Es lo primero porque es deuda presente, y porque hace que todo lo que venga después sea un
cambio en **un** lugar en vez de cuatro. Hoy `Store` ya es una clase única
(`world/store.py`, cadena de mixins sobre `LinkedStores`), pero habla el idioma de sldb sin
tipo: `(model, name, store)` y strings.

### 3.1 La dirección deja de ser string

`export_id: str` → `DocId` frozen (`store | None`, `model`, `name`), parseado una vez en el
borde. Hoy hay **13 pares** `foo(model, name, store)` / `foo_of(export_id)` en
`world/storage/`: la misma operación escrita dos veces. Con `DocId` queda una.
`split_id`/`join_id` (`kernel/ids.py`) pasan a ser sus constructores.

### 3.2 La política por modelo, tipada y en un solo lugar

Hoy "qué se hace con los documentos de tal modelo" está en cinco sitios que no se enteran
entre sí:

| constante | dónde | qué decide |
|---|---|---|
| `LEDGER_MODEL = "MoveDoc"` | `world/graph_file.py:13` | qué modelo se excluye de la frescura del grafo |
| `INTERNAL_MODELS` | `world/lexicon_parts/vocabulary.py:19` | qué modelos no son sustantivos del léxico |
| `UNSUGGESTED_MODELS` | `world/lexicon_parts/vocabulary.py:22` | qué modelos no ofrecen valores |
| `exclude_tags=("type.pron.move",)` | `world/world.py:104,134` | qué documentos no entran al grafo |
| `IndexProjection.models` | `corpus/index_projection.py` | qué modelos entran al corpus |

Pasa a ser una declaración por modelo, con el tipo pydantic adentro: si entra al grafo, al
léxico, al corpus; cuál es su texto representativo; si es el ledger. El `Store` la consulta;
nadie más decide. Como el `RuntimeDocument` de sldb ya trae el `model_type`, la lectura
puede devolver el pydantic en vez de `dict`.

Sobre el tipado: hoy nada de esto lo ve mypy, porque `pyproject.toml` tiene
`follow_imports = "skip"` + `ignore_missing_imports` para `sldb.*` y `kgdb.*` — todo lo que
entra por sldb es `Any`. Esta declaración es el punto donde el tipo vuelve a existir del lado
de pron sin esperar a que sldb se tipe. (Y `sldb.api`, de hoy, es la otra mitad de eso.)

### 3.3 El Store toma las tres capas

Una sola noción de frescura sobre las tres. Arregla tres defectos que hoy conviven:

- **Federación**: `model_hashes()` (`world/world_declaration.py:44`) mira solo el store
  local, pero `hash_mundo()` (`world/fingerprint.py:31`) sí incorpora el `hash_a` de cada
  enlazado. En un mundo federado `refresh_if_stale()` dice "fresco" aunque un store enlazado
  se haya movido: el léxico se entera, el grafo no.
- **Alcance dispar**: el grafo es local-only (kgdb llama `load_runtime_documents(sp, …)` sin
  `include_linked`, y el export de sldb recorre solo los modelos del índice local); el corpus
  sí federa (`world/storage/document_reader.py:32`).
- **Nadie las refresca junto**: `World.refresh()` reconstruye solo el grafo; el corpus se
  refresca perezoso adentro de `rank()`, auditando todos los documentos en cada llamada.

Además el corpus **no está cableado en `src/`**: `Corpus(...)` solo aparece en `tests/`.
Esta fase es también la decisión de si es parte del mundo o una derivada del consumidor
(lo que hoy sugiere `derived_dir`).

### Cómo se ejecuta

Expandir y después colapsar, cada fase compilando y con la suite verde:

1. **Expandir**: `DocId`, la declaración por modelo y la capa de frescura nacen al lado de lo
   viejo; los `foo_of()` y las cinco constantes siguen, delegando.
2. **Colapsar**: se borran los `_of()`, las constantes y `GraphRefresher` como puerta aparte.

## 4. Fase 2 — el documento es una proyección (repo: **sldb v1**) · vale en A y en B

`selfdoc` ya demuestra la tesis entera: un documento **no** es un markdown, es la proyección
de una fuente. Un `PythonSymbolDoc` tiene fuente (el símbolo del AST), fingerprint de esa
fuente (`source_sha256`, `source_span`) y campos autorados encima. El markdown es dónde se
materializa, no qué es.

```
Source  ──scan──▶  facts (tipados)  ──project──▶  Document  ──render──▶  markdown
```

Lo que falta para "cualquier cosa proyectable a AST" es un protocolo, no un motor: un
`Scanner` con `supported_extensions` + `scan(path) -> list[Facts]` — exactamente lo que el
`ScannerPlugin` muerto de `core/ingest/` intentaba ser. El scanner de TypeScript hay que
**reescribirlo**, no revivirlo.

Por qué acá y no en kimun: el scanner de Python, el modelo, el materializador y la validación
de aristas ya están escritos en v1 y funcionando. En kimun esto es S1 + parte de S2, que no
han empezado. Y el contrato que sale de esta fase (qué es una fuente, qué es un fingerprint
de fuente, qué campo es derivado y cuál autorado) es el mismo que v2 necesita: en kimun eso
es el `:fingerprint` externo de `02 §6.4` (decisión 11: el kernel valida la forma
`<alg>:<hex>` y compara; qué bytes se digieren es contrato del motor emisor — o sea, del
scanner). Escribirlo acá no es trabajo tirado en ninguno de los dos escenarios.

Lo que retira cuando llegue: el tracking centrado en `path` (`DocumentEntry.path`) y `hash_c`
como hash del texto markdown.

## 5. Fase 3 — kgdb adentro del store (repo: **sldb v1**) · acá se decide A o B

Es el eslabón más barato, y la razón es verificable: **el grafo ya es una función pura del
store**. `build_typed_snapshot` se alimenta enteramente de `export_kgdb_semantic_payload`;
los `RelationTypeDoc` y `RelationDoc` ya son documentos de sldb. Las aristas **ya viven en el
store**; lo único que vive afuera es su **índice** (`.pron/graph.nx.json`).

Entonces "mergear kgdb" = que ese índice sea un índice del store, como `sections` y
`semantic` — que desde merkle capa 5–7 ya son shards por documento. No es fusionar dos
productos: es mover un cache adentro, por el camino que la capa 5 ya abrió.

Lo que hay que hacer:

- **Matar `kgdb_sync.py`**: sincroniza por `subprocess` llamando al binario `kgdb`. Es el
  acoplamiento más frágil de la cadena y hoy ya es innecesario — kgdb pasó a `sldb.api` este
  mismo día.
- **Mover el índice de aristas al store**: `contains`, `imports`, `references` (las de
  `python_relation_registry.RELATIONS`) más las estructurales de `kgdb.ingest.typed`
  (`has_field`, `has_document`, `has_model`, `has_section`, `extends`, `names`, `tagged_as`,
  `semantic_parent`, `semantic_equivalent`, `applies_to_*`).
- **Retirar**: `.pron/graph.nx.json`, networkx, `kgdb ingest`, `GraphRefresher`, y la
  asimetría de frescura que la Fase 3.3 tuvo que parchear.

**Por qué acá se decide**: terminar esta fase deja a v1 con documentos-como-proyección y
aristas-como-índice-del-store. Eso es el 80% de la tesis de v2 sobre el sustrato de v1
(archivos + hashes en cadena) en vez del de kimun (nodos content-addressed + árboles de
posiciones). Si se llega hasta acá, el escenario B dejó de ser una opción y pasó a ser un
hecho, y `kimun migrate --from-v1` migra desde un v1 que ya no se parece al que la migración
supone. Antes de empezar esta fase hay que decidir, explícitamente, cuál de los dos caminos
es.

## 6. Fase 4 — v2, en cualquiera de los dos escenarios

Lo que queda de v1 cuando las fases 1–3 están hechas, contra lo que kimun ya construyó:

| v1 después de las fases 1–3 | kimun | hito kimun |
|---|---|---|
| archivo markdown trackeado por `path` | nodo S/M/G en el pool content-addressed | kernel 0–4 (cerrado) |
| `hash_c` / `hash_d` por documento | id content-addressed del nodo | kernel 1 (cerrado) |
| `hash_b` por modelo, `hash_a` por store, shards por documento | árboles de posiciones con Merkle perezoso | kernel 3 (cerrado) |
| modelos pydantic registrados | modelos como nodos del árbol (descriptores EDN opacos) | **S1, sin empezar** |
| `RelationTypeDoc` / `RelationDoc` + índice en el store | aristas tipadas con evidencia | kernel 2 (cerrado) |
| guarda de escritura por `hash_c` | `TransactionPlan` con 7 chequeos | kernel 4 (cerrado) |
| documento como proyección de una fuente | `:fingerprint` externo + aristas `derived` | kernel 5a/5b (cerrado) |
| `AnchorDoc` de pron (`kind=expr`) | gramática por defecto en `resources/grammar/` | **S7, sin empezar** |
| evaluador de pron | evaluador anclado | **S4, sin empezar** |

Lo cerrado en kimun es **el kernel**. Lo que falta es **el producto** (S1–S7), que es
justamente lo que v1 ya tiene funcionando. Esa asimetría es la que hay que resolver, y es la
decisión de §2.

Si el escenario es A, sigue valiendo la regla de `08 §1`: la migración se prueba sobre una
copia en un directorio temporal, **nunca in place**, y **no se borra código de pron** —
sigue vivo mientras `kinesis` lo importe.

## 7. El orden

1. **Fase 1, en pron, ahora.** Es deuda presente (bugs de federación abiertos, política
   duplicada en cinco sitios) y vale igual en A y en B.
2. **Fase 2, en sldb v1.** El contrato de proyección; el scanner genérico. Vale en A y en B.
3. **Decidir A o B.** Antes de la Fase 3, no después.
4. **Fase 3 según lo decidido.** En B, el índice de aristas entra al store. En A, se congela
   de verdad —esta vez con tasks, no con un tag— y arranca S1 en kimun.

## 8. Lo que queda por decidir

- **A o B** (§2). Es la decisión grande y no tiene fecha límite técnica, pero sí una
  práctica: cada semana que kimun no se mueve y v1 sí, B se vuelve más cierto por omisión.
  Decidirlo por omisión es la peor de las tres opciones.
- **El corpus**: ¿parte del mundo, o derivada del consumidor? Bloquea el alcance de la
  Fase 3.3.
- **Hasta dónde se tipa la lectura**: ¿el `Store` devuelve el pydantic del modelo, o sigue
  devolviendo `dict` y el tipo vive solo en la declaración por modelo? Lo segundo es menos
  trabajo y sobrevive mejor al escenario A, porque allá el payload no es un `dict` de
  pydantic sino un nodo.
- **Scanners en v1**: ¿se reescribe el de TypeScript ahora, o la cadena código→documento se
  queda en Python hasta que A o B se resuelva?
