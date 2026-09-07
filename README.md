# pron

Base de conocimiento de provenance: átomos, anclas, specs de dominio, corpus (`source/knar`),
revisiones, vistas y el estado operativo de `desk/`. Es **datos**, no herramienta. El nombre es
Mapudungun: el cordel anudado con que se llevaba el registro.

La operan dos herramientas, ninguna vive aquí:

| herramienta | qué hace con esta KB | repo |
|---|---|---|
| `knowledge` (v1, Python) | evaluador anclado s-expr y ops de escritura sobre `.sldb/` v1 + kgdb; se corre con `cd` en este directorio (`python -m knowledge …`, `knowledge-cli …`) | `jpcosec/knowledge` (`~/proyectos/legos/knowledge`) |
| `kimun` (v2, Clojure/bb) | sucesor: `kimun migrate --from-v1 .sldb` la convierte a un store `.kimun/` (hito S2) | `jpcosec/kimun` (`~/proyectos/kimun`) |

## Layout

- `knowledge/` — el *workspace* de documentos de conocimiento que declaran los modelos v1 (`__semantics__["workspace"]`): `atoms/` (los átomos), `anchors/` (los 13 anchors de la gramática del evaluador, documentos `AnchorDoc`), y `facts/`, `propositions/` cuando se creen
- `source/` — `spec/`, `knar/`, `reviews/`, `human_feedback*/`, `diagramas/`, salidas de subagentes
- `views/` — proyecciones (spec2viz)
- `desk/`, `runs/` — estado deskops y evidencia de ejecución
- `.sldb/` — store v1 (modelos, índices, grafo); `store_index.yaml` referencia modelos de `deskops`, `sldb`, `kgdb` y `knowledge` por ruta absoluta (deuda v1)

## Historia

Extraído el 2026-09-07 de `legos/knowledge` con `git filter-repo` (historia preservada, rutas
intactas). El código de la herramienta v1 se
quedó allá.
