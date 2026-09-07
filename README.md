# pron

**Base de conocimiento de provenance + el evaluador que la opera**, en un solo paquete Python.
El nombre es Mapudungun: el cordel anudado con que se llevaba el registro.

- `src/pron/` — evaluador anclado de s-expressions sobre un store `.sldb` v1 (`sldb`) y su grafo
  (`kgdb`): `core/` (sexpr, anchors, resolution, evaluator, session), `ops/` (read, write,
  anchor_add), `bridges/` (sldb, kgdb, write_models), `infra/` (projector), `cli/`.
- `knowledge/` — el *workspace* de documentos que declaran los modelos v1
  (`__semantics__["workspace"]`): `atoms/` (los átomos), `anchors/` (los 13 anchors de la
  gramática), `facts/` y `propositions/` cuando se creen.
- `source/` — `spec/`, `knar/`, `reviews/`, `human_feedback*/`, `diagramas/`, salidas de subagentes.
- `views/`, `desk/`, `runs/` — proyecciones spec2viz, estado deskops, evidencia de ejecución.
- `.sldb/` — store v1 (modelos, índices, grafo). `store_index.yaml` referencia modelos de
  `deskops`, `sldb` y `kgdb` por ruta absoluta (deuda v1).

## Uso

```bash
pip install -e ~/proyectos/legos/pron     # depende de sldb y kgdb (editables del ecosistema)
cd ~/proyectos/legos/pron                 # la raíz operativa es el cwd
pron anchors                              # o: python -m pron anchors
pron list atom
pron check atom "<atom-id>" --summary
pron project                              # regenera el grafo (.sldb/runtime/knowledge.nx.json)
```

La sesión pendiente (`next`) vive en `.pron/session.json`, ignorada por git.

## Quién lo usa

| consumidor | cómo |
|---|---|
| `kinesis` (`~/proyectos/legos/kinesis`) | `import pron`: su `KnowledgePort` se conecta a esta KB |
| `kimun` (`~/proyectos/kimun`, Clojure/bb) | sucesor v2: porta la lectura del evaluador (S4) y migra `.sldb/` a `.kimun/` (S2) |

## Tests

```bash
python -m pytest -q tests     # aceptación, compliance de átomos, wrapper, write ops, anchor add, refresh
```

## Historia

El evaluador nació como `src/knowledge` dentro de `jpcosec/knowledge` (2026-09-03 → 09-07) y se
fusionó aquí el 2026-09-07 con su historia (`git filter-repo` + merge). Ese repo queda como
legacy: el CLI de julio sobre archivos (`knowledge_legacy.py`) y la rama `iso-lab/knowledge`.
