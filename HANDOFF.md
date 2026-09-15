# Handoff — pron, sldb, kgdb y kinesis

Estado al 2026-09-09, fin de la sesión. Todo pusheado.

| Repo | HEAD | Suite |
| --- | --- | --- |
| pron `~/proyectos/pron` | tag `1.0.0` (HEAD `6790d99`) | 98 passed |
| kinesis `~/proyectos/legos` | rama master de legos, tag de cierre al aterrizar M4; el paquete vive en `legos/` (plan 2) | 98 passed, 1 skipped |
| sldb `~/proyectos/hum-ecosystem/tools/sldb` | `50c2fd8` | 441 passed, 1 fallo previo de estilo (`knowledge_surface.py`, tres clases en un archivo) |
| kgdb `~/proyectos/hum-ecosystem/tools/kgdb` | `1247139` | 41 passed |

El commit `6790d99` (antes `5a08497`, "wip") trae: validación `$created`-antes-de-`create` en `Session._compose`/`_plan_compose` (`tests/test_composition_validation.py`), endurecimiento mypy en `session.py`/`resolve.py`/`surface/interpret.py`, un `Makefile` y el pin de extras `dev` en `pyproject.toml`.

Nota de rutas: pron ya no vive dentro del monorepo legos; está en `~/proyectos/pron` y legos lo consume por path (`${PRON_DIR:-../pron}`).

## Qué es cada cosa

- **sldb** es la base de datos direccionable: `st.{Modelo+}.doc.campo` más `--where`, `fields update`, todo por índices y hashes en cadena (`hash_a` del store, `hash_b` por modelo, `hash_c` por documento). Ver `README.md` §"Read and write by address" y §"Caches".
- **kgdb** tipa las relaciones con `RelationTypeDoc` y `RelationDoc`, documentos de sldb, y arma un `MultiDiGraph` con `kgdb ingest --store`.
- **pron** es el SHRDLU sobre un mundo: sustantivos = direcciones de sldb, verbos transitivos = tipos de relación de kgdb, verbos de acción = escrituras de sldb. Spec en `source/spec/`, once capítulos; el 09 y 09a son la conversación de aceptación sobre el mundo del restaurante (`tests/worlds/restaurant.py`).
- **kinesis** monta un agente sobre `ExecutableNode`; su puerto de conocimiento habla con pron (`legos/src/legos/bridges/pron_knowledge.py`). Documentación de esa integración en `legos/docs/configuracion-base-agente/10-conocimiento-via-pron.md`.

Doctrina que no se negocia: pron nunca filtra payloads en Python, nunca ensambla aristas, nunca tiene código por modelo; un mundo agrega palabras con `AnchorDoc` y verbos con `RelationTypeDoc`. pron no tiene átomos. Todo lo declarado va en inglés por ahora (spec 11 §0).

## Lo hecho hoy, en orden

1. **Correcciones de la revisión** (pron `ba37487`): corrección tras un turno missing ("on the terrace"), prevalidación del movimiento completo antes de la primera escritura (con el evaluador `--where` de sldb sobre payloads pendientes), undo con guardas por `hash_c`, permisos dentro de alias compuestos, la proyección corta los alias, segunda lectura de `hash_mundo` antes de ejecutar. `tests/test_06_review.py`.
2. **Complementos nominales** (`bc16543`): "the reservations of Luis Soto", "Luis Soto's reservations for Friday", anidados; resuelven por relación cruzando aristas de kgdb con predicados de sldb.
3. **Sesiones de solo lectura** (`8d415bf`, `77ebac9`): `Session(read_only=True)`; los alias de acción fuera de las acciones permitidas no entran al léxico.
4. **Kinesis**: permisos como alcances de proyección, lecturas por sesión de solo lectura, una sesión por ejecución (`9f6a423`), backend sobre `pron serve` (`f167bea`, `66498ec`).
5. **Velocidad, en sldb** (`1c39c2b`, `67c0cd0`, `0cc2979`, `50c2fd8`): cachés por la cadena de hashes (índices en memoria con copias, documentos extraídos en memoria por store y por documento, `.sldb/runtime/cache/extracted.json` y `built.json` en disco), reindexados que bajan solo por el modelo cuyo `hash_b` se movió, `stores update` incremental, sin reescritura del layout al abrir, libyaml para los índices. Un `stat` por documento detecta ediciones a mano; `SLDB_TRUST_CHAIN=1` lo salta.
6. **pron sin networkx en lectura** (`0bc5f64`), ids de movimiento únicos contra el store (`a6cf9bf`).
7. **`pron serve`** (`18defed`, spec 11 §8): un proceso mantiene el mundo abierto tras `<mundo>/.pron/serve.sock`; `say`, `repl` y kinesis lo usan si contesta; `--local` lo evita; `pron.client` es solo biblioteca estándar.

8. **Mundos y stores** (después del handoff inicial): un `ProjectionDoc` puede estar `exposed`, y esa es la interfaz de un mundo hacia otros; plantillas de mundo (`pron init --template`); cada turno registra lo que leyó con su `hash_c` (`record["reads"]`); `pron serve` abre **un** store y enlaza en él los stores de los demás mundos (`--world otro=../otro`, `--mount`), y cada mundo es una proyección sobre su store: una sesión tiene un hogar (`Session(home="A")`), resuelve con un alcance por store (`A:st.{Reserva+}`, direcciones calificadas en sldb desde `19af4f0`), escribe en el primer store de su proyección y los documentos que escribe nombran los ids como ese store los lee (sin prefijo). Un cliente de otro mundo solo abre proyecciones expuestas y solo dice oraciones. Spec 01 §Un mundo en varios stores, §Interfaz entre mundos, §Plantilla; 02, 03, 07, 12. Tests `test_09_worlds.py`, `test_10_federation.py`.

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

## Pendiente en pron y sldb, por prioridad

1. **Embedder real**: el puerto existe, el fallback es difflib; falta inyectar uno desde la CLI de pron. La otra sesión está trabajando el índice por documento en `embedder.py`.
2. **Enlaces de predicado en prosa** no entran al grafo tipado: la exportación de sldb no los expone.
3. **Escrituras**: lo que queda es real (releer textos para mover la cadena, rearmar el grafo entero en kgdb, guardar el índice de secciones del ledger que crece por turno). Si hace falta bajar de 0,4 s, el candidato es un ingest incremental en kgdb.
4. **Higiene**: lock de revisiones de sldb, kgdb y pron (hoy editables desde carpetas vecinas), CI que corra las suites, y pushear.

Kinesis lo lleva otro agente. Lo que pron le ofrece está en el spec 12 y no cambia sin ese capítulo: `Session(read_only=..., home=...)`, `Response` en `pron.response`, `pron.client` (`socket_path`, `alive`, `request`, `RemoteSession` con `world` y `home`, `RemoteGraph`, `RemoteWorld`), `World.store.payload`, y el socket en `<mundo>/.pron/serve.sock`. Aviso para ese agente: los ids de exportación ahora pueden llevar store (`A:Modelo:doc`) cuando la sesión habla a través de un daemon; `pron.ids` los parte. Las firmas viejas siguen valiendo con sus defaults. Sus cambios de hoy en kinesis (`9f6a423`, `f167bea`, `66498ec`, y la documentación en `docs/configuracion-base-agente/10-conocimiento-via-pron.md`) quedaron comiteados ahí; lo que siga en ese repo es de ese agente.

## Decisiones abiertas

- `pron serve` atiende de a una petición y no autentica: el socket es local y habla como el hablante que el cliente dice ser (spec 11 §6). Quién puede tocar el socket es de la aplicación.
- El barrido de `stat` por documento en sldb es la concesión al Markdown editado a mano; si un store solo se escribe por sldb, `SLDB_TRUST_CHAIN=1`.

## Memoria de la sesión

Notas persistentes en `~/.claude/projects/-home-jp-proyectos-legos/memory/`: doctrina de pron, no atoms, inglés por ahora, la regla Merkle de las cachés, y la lección de no borrar todo lo sin trackear.

## Checkpoint 2026-09-14: vocabulario de símbolos Python (iteraciones 1–3)

Estado de la sesión sobre el trabajo previo sin commitear (`source_symbols.py`, `source_graph.py`, merges en `world.py`/`graph.py`/`verbs.py`/`display.py`/`lexicon.py`/`resolve.py`/`session.py`). Workspace sucio preservado; sin reset ni checkout destructivos.

Correcciones sobre lo entregado antes:

- `is_node` no exige grafo: `display.name` consultaba `graph.load()` en mundos sin `.pron/graph.nx.json` (daemon de federación) y reventaba con `FileNotFoundError`; cascada que rompía tres tests de `test_10_federation.py` y el REPL de `test_05`. Ahora `source_symbols.is_node` pasa por `graph.available()`.
- `source_symbols.name` no deja punto colgante en nodos de módulo (`sample..` → `sample`).
- Nodos del grafo fuente: `python_symbol`, `python_module` y `python_external` participan como sustantivo de sólo lectura; los endpoints externos se rotulan desde su id (`pydantic.BaseModel`).

Iteración 1 — pruebas de las tres relaciones (`tests/test_01_world.py::test_source_contains_and_imports_answer_through_pron`): `references` inversa (ya cubierta), `contains` (módulo → declaración) e `imports` (importer → importado, con endpoint externo). Cada caso verifica que la respuesta sale de la sesión de Pron y que la traza registra `pron graph ...` / `kgdb edges...`, nunca lectura directa del JSON generado.

Iteración 2 — dirección directa sin parser paralelo: `what python symbols does CommandRecord reference` funciona. Dos piezas: los verbos fuente registran su forma no flexionada (`reference`/`import`/`contain`) como palabras de la misma relación, y `_c_read_relation` reconoce el auxiliar `does/do` sólo para relaciones `source_relation:*` (el agente de un verbo AST es el origen de la arista). La regla auxiliar no toca relaciones de store pasivas: `what reservations does Ana have?` sigue resolviendo como antes. Además `_value_word_suggestions` ya no consulta schema de modelos virtuales (`PythonSymbol` no está registrado en el store).

Iteración 3 — nombres propios exactos: la resolución por substring es último recurso. Nuevo orden en `source_symbols.resolve`: (1) identidad exacta — `ast.name`, `module.name`, id de nodo y su segmento final (`ParserScanner.scan`); (2) substring. Los nombres punteados llegan como un solo token gracias a `_merge_dotted` en `surface/interpret.py` (une `word/unknown` separados por `.` sin espacios; no toca números). La ambigüedad exacta pregunta "Which one?" con candidatos calificados por módulo; `sldb.sldb.selfdoc.command.CommandRecord` resuelve exacto.

Validación de la sesión: `python -m pytest -q tests/` → 121 passed, 0 failed (incluye `test_05...::test_own_knowledge_base_is_derived_from_the_repo`). Interfaz real contra el mundo SLDB tras `pron refresh`: las tres relaciones responden con traza limpia. `sldb selfdoc python-check` → `ok: true`, `kgdb_stale: []`, `written: 0`; `sldb stores check` → PASS.

Pendiente (mismo orden del handoff previo): 4 proyecciones (`ProjectionDoc` explícito para exponer/ocultar `PythonSymbol`, read-only siempre), 5 aliases curados (`AnchorDoc.ref` con `source:<python-node-id>`), 6 federación de símbolos fuente por addressing de store, 7 documentación del spec SLDB al cerrar cada capacidad (`contains/imports/references` son hechos AST, no `RelationDoc`; sin certezas sobre imports dinámicos, star imports, reexports ni shadowing).
