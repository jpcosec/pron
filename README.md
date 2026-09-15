# pron

## ¿Qué es pron?

Un SHRDLU sobre un mundo que ya existe. Los documentos de sldb son los objetos, los modelos de relación de kgdb son los verbos transitivos, las escrituras de sldb son los verbos de acción. pron convierte oraciones en direcciones, aristas y escrituras, sostiene el diálogo cuando una oración no alcanza, y registra cada movimiento.

El nombre es Mapudungun: el cordel anudado con que se llevaba el registro.

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

```bash
pron init --world . --pythonpath . --knowledge
pron docs --world . --pythonpath .          # spec, comandos, módulos, implements
pron docs --world . --pythonpath . --check  # sin drift
pron check --world . --pythonpath .         # lints, incluido que todo módulo cite un capítulo
pron say "what does the module resolve implement?" --world . --pythonpath .
```

Los átomos de v1 se quedan en la rama `v1-code-and-kb`, como material histórico.

## Capas

| capa | qué hace | dónde |
|---|---|---|
| mundo | abre un store, lee su declaración, refresca su grafo | `world.py`, `store.py`, `graph.py` |
| léxico | deriva las palabras del store y las corta por la proyección | `lexicon.py`, `embedder.py` |
| superficie | clasifica, arma frases nominales, interpreta construcciones fijas | `surface/` |
| sustantivos | dirección + predicados → sldb | `resolve.py` |
| verbos | lee aristas, verifica contra el `RelationTypeDoc`, afirma, transiciones | `verbs.py` |
| kernel | las escrituras de sldb, con guardas y deshacer | `kernel.py` |
| diálogo y ledger | la pendiente, los referentes, el `MoveDoc` por turno | `dialogue.py`, `ledger.py` |
| sesión | el turno entero | `session.py` |

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

- **Colapsar el camino dry-run.** `_dry_parts`/`_plan_compose` duplica a `_execute`/`_compose`
  en `session.py`, y esa duplicación ya produjo un bug. Orden seguro: test de caracterización
  que afirme que ambos caminos coinciden sobre un corpus de oraciones, y recién después
  colapsar el par. La superficie pública (el constructor y `turn()`) ya está clavada por
  spec 12 y `tests/test_12_runtime_surface.py`; no tocarla.
