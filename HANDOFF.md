# Handoff — pron, sldb, kgdb y kinesis

Estado al 2026-09-08, fin de la sesión. Cuatro repos, nada pusheado.

| Repo | HEAD | Suite |
| --- | --- | --- |
| pron `~/proyectos/legos/pron` | `d7f9002` (40 commits sobre `origin/master`) | 68 passed |
| kinesis `~/proyectos/legos/kinesis` | `71f60f3` (sin remoto) | 97 passed, 1 skipped |
| sldb `~/proyectos/hum-ecosystem/tools/sldb` | `50c2fd8` | 441 passed, 1 fallo previo de estilo (`knowledge_surface.py`, tres clases en un archivo) |
| kgdb `~/proyectos/hum-ecosystem/tools/kgdb` | `1247139` | 41 passed |

Los tres últimos commits de pron (`eb6cce1`, `bbecea5`, `d7f9002`: navegación del grafo, `DocumentIndex` de embeddings por documento, `refresh_if_stale`, `tests/test_08_graph_index.py`) son de otra sesión en paralelo; no los escribí y no los describo más allá de sus mensajes. La suite pasa con ellos.

## Qué es cada cosa

- **sldb** es la base de datos direccionable: `st.{Modelo+}.doc.campo` más `--where`, `fields update`, todo por índices y hashes en cadena (`hash_a` del store, `hash_b` por modelo, `hash_c` por documento). Ver `README.md` §"Read and write by address" y §"Caches".
- **kgdb** tipa las relaciones con `RelationTypeDoc` y `RelationDoc`, documentos de sldb, y arma un `MultiDiGraph` con `kgdb ingest --store`.
- **pron** es el SHRDLU sobre un mundo: sustantivos = direcciones de sldb, verbos transitivos = tipos de relación de kgdb, verbos de acción = escrituras de sldb. Spec en `source/spec/`, once capítulos; el 09 y 09a son la conversación de aceptación sobre el mundo del restaurante (`tests/worlds/restaurant.py`).
- **kinesis** monta un agente sobre `ExecutableNode`; su puerto de conocimiento habla con pron (`src/kinesis/agent_zero/bridges/pron_knowledge.py`). Documentación de esa integración en `kinesis/docs/configuracion-base-agente/10-conocimiento-via-pron.md`.

Doctrina que no se negocia: pron nunca filtra payloads en Python, nunca ensambla aristas, nunca tiene código por modelo; un mundo agrega palabras con `AnchorDoc` y verbos con `RelationTypeDoc`. pron no tiene átomos. Todo lo declarado va en inglés por ahora (spec 11 §0).

## Lo hecho hoy, en orden

1. **Correcciones de la revisión** (pron `ba37487`): corrección tras un turno missing ("on the terrace"), prevalidación del movimiento completo antes de la primera escritura (con el evaluador `--where` de sldb sobre payloads pendientes), undo con guardas por `hash_c`, permisos dentro de alias compuestos, la proyección corta los alias, segunda lectura de `hash_mundo` antes de ejecutar. `tests/test_06_review.py`.
2. **Complementos nominales** (`bc16543`): "the reservations of Luis Soto", "Luis Soto's reservations for Friday", anidados; resuelven por relación cruzando aristas de kgdb con predicados de sldb.
3. **Sesiones de solo lectura** (`8d415bf`, `77ebac9`): `Session(read_only=True)`; los alias de acción fuera de las acciones permitidas no entran al léxico.
4. **Kinesis**: permisos como alcances de proyección, lecturas por sesión de solo lectura, una sesión por ejecución (`9f6a423`), backend sobre `pron serve` (`f167bea`, `71f60f3`).
5. **Velocidad, en sldb** (`1c39c2b`, `67c0cd0`, `0cc2979`, `50c2fd8`): cachés por la cadena de hashes (índices en memoria con copias, documentos extraídos en memoria por store y por documento, `.sldb/runtime/cache/extracted.json` y `built.json` en disco), reindexados que bajan solo por el modelo cuyo `hash_b` se movió, `stores update` incremental, sin reescritura del layout al abrir, libyaml para los índices. Un `stat` por documento detecta ediciones a mano; `SLDB_TRUST_CHAIN=1` lo salta.
6. **pron sin networkx en lectura** (`0bc5f64`), ids de movimiento únicos contra el store (`a6cf9bf`).
7. **`pron serve`** (`18defed`, spec 11 §8): un proceso mantiene el mundo abierto tras `<mundo>/.pron/serve.sock`; `say`, `repl` y kinesis lo usan si contesta; `--local` lo evita; `pron.client` es solo biblioteca estándar.

Tiempos en el mundo del restaurante, máquina quieta: abrir sesión 0,06 s; lectura 0,11 s; escritura 0,4–0,6 s; `pron say` en frío 0,45 s, y 0,12 s con `pron serve` corriendo. Al empezar el día eran 0,24 s, 0,5–0,8 s, 3–4,5 s y 1,0 s.

## Cómo correr

```bash
# pron
pron init --world . --pythonpath . --knowledge && pron docs --world . --pythonpath . && pron check --world . --pythonpath .
python -m pytest -q tests                       # ~35 s, mundos reales
pron serve --world . --pythonpath .             # en otra shell: pron say "..." --world .   ·   pron serve --world . --stop
# kinesis
python -m pytest -q tests && ruff check src tests && mypy src
kinesis agent --input examples/agent-goal.json --knowledge-world . --read all
# sldb / kgdb
python -m pytest -q tests
```

Una advertencia: `pron say` sobre el repo de pron deja `MoveDoc`s en `ledger/` y mueve `.sldb/`. Para probar a mano usá un mundo aparte (`build_restaurant` en un directorio de scratch). Si limpiás, borrá por ruta explícita (`ledger/move-2026*.md`), nunca todo lo sin trackear.

## Pendiente, por prioridad

1. **Extremo a extremo de kinesis con pron.** Los tests corren sobre copias del store; nunca se corrió `kinesis agent --knowledge-world .` con un replay ni con Gemini.
2. **Palabras del mundo de kinesis.** Faltan `AnchorDoc` para state, machine, transition, agent, tool, port; sin ellos el agente solo nombra por identificador. Y un `ProjectionDoc` para el agente: hoy usa `all`, que en escritura permite todo.
3. **El operador Gemini** sigue pidiendo referencias `Modelo/Documento`; debería recibir el léxico (`pron lexicon --json`) y decidir con oraciones.
4. **Transiciones de kinesis como `RelationDoc`** en el mundo, no solo en `.kinesis/machine.json` (capítulo 7 de sus docs).
5. **Sacar `AtomDoc` de deskops del store de kinesis**; `pron check` lo marca.
6. **Embedder real**: el puerto existe, el fallback es difflib; falta inyectar uno desde la CLI de pron y de kinesis. La otra sesión está trabajando el índice por documento en `embedder.py`.
7. **Enlaces de predicado en prosa** no entran al grafo tipado: la exportación de sldb no los expone.
8. **Escrituras**: lo que queda es real (releer textos para mover la cadena, rearmar el grafo entero en kgdb, guardar el índice de secciones del ledger que crece por turno). Si hace falta bajar de 0,4 s, el candidato es un ingest incremental en kgdb.
9. **Higiene**: lock de revisiones de sldb, kgdb, deskops y pron (hoy editables desde carpetas vecinas), CI que corra las cuatro suites, y pushear.

## Decisiones abiertas

- Lectura y escritura de una misma ejecución de kinesis usan sesiones distintas; una pregunta abierta en una lectura no la cierra una escritura.
- `pron serve` atiende de a una petición y no autentica: el socket es local y habla como el hablante que el cliente dice ser (spec 11 §6). Quién puede tocar el socket es de la aplicación.
- El barrido de `stat` por documento en sldb es la concesión al Markdown editado a mano; si un store solo se escribe por sldb, `SLDB_TRUST_CHAIN=1`.

## Memoria de la sesión

Notas persistentes en `~/.claude/projects/-home-jp-proyectos-legos/memory/`: doctrina de pron, no atoms, inglés por ahora, la regla Merkle de las cachés, y la lección de no borrar todo lo sin trackear.
