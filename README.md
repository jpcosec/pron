# pron

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
pron lexicon --world . [Model]              # qué se puede decir · los verbos de una clase
pron say "the large tables on the terrace" --world . --trace
pron repl --world . --speaker me
pron check --world .                        # los lints
```

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

## Depende de

- [sldb](https://github.com/jpcosec/hum-ecosystem) con el surface de direcciones y el `hash_b` móvil (commits `e7a2c0c`, `cf0073d`).
- [kgdb](https://github.com/jpcosec/hum-ecosystem) con relaciones tipadas (`kgdb init`, `kgdb ingest --store`, commit `1247139`).

## Quién lo usa

`kinesis` declara `pron` como dependencia y su `KnowledgePort` importa la API de v1. Hasta que se adapte, kinesis tiene que apuntar a la rama `v1-code-and-kb`.
