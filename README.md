# pron

## ¿Qué es pron?

Un SHRDLU sobre un mundo que ya existe. Los documentos de sldb son los objetos, los modelos de relación de kgdb son los verbos transitivos, las escrituras de sldb son los verbos de acción. pron convierte oraciones en direcciones, aristas y escrituras, sostiene el diálogo cuando una oración no alcanza, y registra cada movimiento.

El nombre es Mapudungun: el cordel anudado con que se llevaba el registro.

## Cómo funciona

pron no guarda nada del mundo por su cuenta: sldb es el store de documentos (los sustantivos, cada uno con dirección y campos) y kgdb es el grafo de relaciones tipadas (los verbos transitivos, declarados en `RelationTypeDoc` y afirmados como `RelationDoc`). pron traduce entre una oración y esas dos cosas; no tiene su propia base de datos ni su propio esquema.

El diccionario con el que entiende una oración no está escrito en el código de pron: sale de los datos, cada vez que se carga un mundo.

- **Sustantivos** — de los modelos de sldb: el nombre del modelo, sus campos, los valores que ya existen (`lexicon.py`).
- **Verbos transitivos** — de los `RelationTypeDoc` de kgdb: cada tipo de relación declarado se vuelve una palabra-verbo (`booked_by`, `implements`), en modo lectura o lectura-y-afirmación según lo que la proyección permita.
- **Verbos de acción** (`create`, `change`, `add`, `remove`, `forget`…) y la gramática (`the`, `it`, `who`, `on`) son lo único fijo de pron, iguales para cualquier mundo (spec 04, 11 §0).

Un turno (`Session.turn`, spec 06/07/11) sigue siempre el mismo camino:

1. **Interpretar** — la oración se tokeniza y se prueba contra un puñado fijo de construcciones (crear, cambiar, preguntar, deshacer…) hasta que una calza.
2. **Bajar a formas** — lo entendido se escribe como una s-expression (spec 13): `(create Reservation (party_size 6))`, `(assert booked_by … …)`. Es un lenguaje intermedio, chico y sin ambigüedad — el mismo que produciría un click en `graph_ui` en vez de una oración escrita. Todo lo que sigue trabaja sobre esta forma, no sobre la oración original.
3. **Resolver los sustantivos** — cada frase nominal de las formas se convierte en direcciones concretas de sldb (`find --where`, un referente como "it", o una dirección exacta). Si hay ambigüedad, se abre una pregunta pendiente en vez de adivinar.
4. **Prevalidar** — antes de escribir nada, se simula el movimiento completo (coerción de tipos, transiciones de estado, condiciones de las aristas) contra una copia en memoria; si algo fallaría, no se toca el store.
5. **Ejecutar** — recién ahí se escribe de verdad: `docs create`, `fields update`, un `RelationDoc` nuevo.
6. **Refrescar** — el grafo de kgdb se reconstruye a partir de lo que sldb acaba de guardar.
7. **Registrar** — todo el turno (qué se leyó, qué se escribió, el hash del mundo antes y después) queda en un `MoveDoc` (el ledger); ahí se apoya "¿por qué?".

El estado propio de una sesión es mínimo: si hay o no una pregunta pendiente, y los referentes recientes ("it", "the previous one"). Nada más persiste entre turnos que no esté ya en sldb o en el ledger.

Afuera de pron: **sldb** (el store de documentos y direcciones), **kgdb** (el grafo de relaciones tipadas, derivado y de solo lectura), **graph_ui** (otra superficie, gestos en vez de oraciones, que produce las mismas formas de spec 13) y **legos** (consume pron como librería, sin pasar por ninguna superficie — ver §Quién lo usa).

Las capas de código que implementan cada paso están en la tabla de la siguiente sección (§Capas); una versión dibujada de este mismo recorrido, con un turno completo de ejemplo, está en [`docs/spec2viz`](docs/spec2viz/README.md) (`offline.html`, sin dependencias de red).

## Estado

v2, implementada desde [`source/spec/`](source/spec/README.md) en septiembre de 2026. Los nueve pasos del orden de construcción están hechos; la conversación del spec 09 sobre el mundo del restaurante corre entera en los tests. La v1 sigue en la rama `v1-code-and-kb` y el tag `v1-frozen`.

Lo que un mundo declara está en inglés por ahora (spec 11 §0); la prosa del spec está en español.

## Probar

```bash
pip install -e .            # sldb y kgdb del ecosistema, instalados editables
python -m pytest -q tests   # cada test monta un mundo real desde cero
```

## Usar

Un mundo es un store de sldb. Sobre cualquier store:

```bash
pron init --world . --pythonpath .          # kgdb init + los modelos de pron
pron refresh --world .                      # índices de sldb + grafo tipado de kgdb en .pron/
# Derivados, fuera de git: .pron/ (grafo, vectores) y .sldb/runtime/cache/ (payloads extraídos por sldb)
pron lexicon --world . [Model]              # qué se puede decir · los verbos de una clase
pron say "the large tables on the terrace" --world . --trace
pron repl --world . --speaker me
pron serve --world . [--world otro=../otro]  # un store abierto, el de ., con ../otro enlazado como mundo 'otro'; say, repl y los runtimes hablan por .pron/serve.sock
pron serve --world . --mount tercero=../tercero   # agrega un mundo a un daemon corriendo
pron serve --world . --stop
pron init --world . --template DIR          # un mundo nuevo con las palabras, proyecciones y relaciones de la plantilla
pron check --world .                        # los lints
```

Un turno frío cuesta medio segundo, casi todo imports y la primera carga del store; con `pron serve` corriendo, `pron say` lee en 0,12 s y escribe en medio segundo, y el proceso que pregunta no importa ni sldb: el cliente es `pron.client`, solo biblioteca estándar.

## Un mundo se declara con documentos

Un mundo se declara con documentos, nunca con código de pron: modelos `StructuredNLDoc`, `RelationTypeDoc` de kgdb para los verbos, `RelationDoc` para las aristas, `AnchorDoc` para las palabras, `ProjectionDoc` para lo que una sesión puede nombrar. El ejemplo completo está en [`source/spec/09a`](source/spec/09a-el-mundo-del-restaurante.md) y montado como fixture en `tests/worlds/restaurant.py`.

## La KB de pron

Este repo es también un mundo, y no tiene átomos. Su conocimiento sobre sí mismo ya tiene forma: los capítulos de `source/spec/`, trackeados donde viven como `SpecDoc` con sus secciones indexadas por sldb; los `CliCommandDoc` y `SurfaceDoc` generados del código; y las aristas `implements` de cada módulo hacia los capítulos que su docstring cita. Todo eso lo produce `pron docs` y nada se mantiene a mano.

Solo se versiona lo que se escribe: los capítulos, las explicaciones, las anclas, las proyecciones y el ledger. El store (`.sldb/`), los tipos de relación (`kgdb/`, `knowledge/relations/`) y los documentos generados (`knowledge/surfaces/`, `knowledge/commands/`) son derivados y no están en git: `make world` los reconstruye desde el repo, y `make docs-check` los reconstruye y falla si el README generado no coincide con el versionado.

```bash
make world                                  # sldb stores init + pron init --knowledge + pron docs
pron docs --world . --pythonpath .          # spec, comandos, módulos, implements
pron check --world . --pythonpath .         # lints, incluido que todo módulo cite un capítulo
pron say "what does the module resolve implement?" --world . --pythonpath .
```

Los átomos de v1 se quedan en la rama `v1-code-and-kb`, como material histórico.

## Capas

| capa | qué hace | dónde (`src/pron/`) |
|---|---|---|
| primitivas | los datos del turno, el lector de formas, los verbos de acción y el kernel que escribe en sldb con guardas y deshacer | `kernel/` (`parts/`, `sexp/`, `actions/`, `kernel.py`) |
| mundo | abre un store, lee su declaración, refresca su grafo | `world/world.py`, `world/store.py`, `world/graph.py` |
| léxico | deriva las palabras del store y las corta por la proyección | `world/lexicon.py`, `world/matching/` |
| superficie | clasifica, arma frases nominales, interpreta construcciones fijas | `surface/` |
| formas | la forma leída se compila a partes | `sexpr/forms/` |
| sustantivos y verbos | dirección + predicados → sldb; aristas, `RelationTypeDoc`, condiciones, transiciones | `sexpr/resolving/` |
| el movimiento | planificar, prevalidar, ejecutar por tipo de parte | `sexpr/planning/`, `sexpr/prevalidation/`, `sexpr/execution/` |
| diálogo y ledger | la pendiente, los referentes, el `MoveDoc` por turno | `sexpr/dialogue/`, `sexpr/turn/ledger.py` |
| sesión | el turno entero | `session.py`, `sexpr/turn/` |

## Como librería para un runtime

Un runtime que ya tiene su propio parser (un LLM, por ejemplo) no necesita la superficie de pron, pero sí lo que hay debajo, para no armar su propio grafo ni su propio índice:

- `World(root, pythonpath)`: abre el mundo; `refresh()` reconstruye el grafo tipado (`stores update` + ingest de kgdb, por librería) y `refresh_if_stale()` solo cuando los `hash_b` de los modelos cambiaron; `derived_dir` es `.pron/`, fuera de git, para lo que el consumidor derive.
- `World.store` (`Store`): la única puerta a sldb: documentos cacheados, `find(scope, where)`, `matches`, `schema`, y escrituras con roundtrip (`create`, `update_field`, `append`, `untrack`).
- `World.graph` (`Graph`): lee el grafo persistido sin networkx. Además de `edges_from`/`edges_to`: `nodes_of_type`, `targets`/`sources`, `roots(node_type, relation)`, `children`/`parent`/`descendants` (por defecto sobre `semantic_parent`) y `neighbors_via(node, relation, exclude_prefixes=...)` para hermanos por tag. Todo parametrizado por nombre de relación; pron no sabe cuáles declara un mundo.
- `DocumentIndex(Matcher(embedder), cache_path)`: documentos rankeados por similitud. `index([(key, hash, text)])` embebe solo lo que cambió y persiste los vectores en un archivo derivado; `rank(query, k, threshold)` devuelve `[(key, score)]`. Sin embedder rankea con difflib y el archivo lo dice.

## Verificar cambios

Con SLDB y KGDB instalados en el entorno:

```bash
python -m pip install -e '.[dev]'
make check          # lint, formato, tipado, tests y documentación
make test           # suite local, sin plugins externos de pytest
make format         # aplica formato; check solo lo verifica
```

También existen `make lint`, `make format-check`, `make typecheck` y `make docs-check`.
Ruff, mypy y pytest tienen versiones fijadas en el extra `dev`. El chequeo de mypy
cubre las anotaciones existentes; todavía no exige tipado estricto en todo pron.
Para regenerar documentación tras un cambio de contrato, usa `pron docs --world . --pythonpath .`.

## Dependencias

- [sldb](https://github.com/jpcosec/hum-ecosystem) fijado al commit `a508034`.
- [kgdb](https://github.com/jpcosec/hum-ecosystem) fijado al commit `5effed5`.

## Quién lo usa

legos declara `pron` como dependencia y habla con esta versión: su `PronWorld` (`legos/src/legos/bridges/pron_world.py`) abre un `World` y lee con forms (spec 13) a través de sesiones de solo lectura y `World.payload`. Un permiso de legos es el nombre de una proyección.

## Next

- **Referentes de una lectura sin ambigüedad.** "what reservations does Ana Pérez have?"
  no deja a Ana Pérez como referente singular; una respuesta elegida en una pendiente sí.
- **kgdb por la CLI de sldb.** pron ya usa `sldb.api`; kgdb todavía llama las clases de la
  CLI de sldb, y por eso `pron init` sigue imprimiendo sus "Registered".
- La superficie pública (el constructor de `Session` y `turn()`) está clavada por spec 12
  y `tests/session/test_12_runtime_surface.py`; no tocarla.
