# KGDB LAYER — Cómo funciona el grafo y cómo consultarlo

## Estado
Documentación operativa verificada contra el código y contra este mismo repo
(pipeline ejecutado end-to-end el 2026-09-06). Complementa `source/spec/GRAPH_ARCHITECTURE.md`.

## Qué es kgdb

El sustrato "tonto" de persistencia y consulta de grafos del ecosistema:
contratos Pydantic + NetworkX + CLI. Cero razonamiento semántico, cero workflow,
cero UI. Define QUÉ forma tiene un grafo válido y CÓMO consultarlo; el
significado lo ponen los productores (sldb, deskops, knowledge).

## Contratos (src/kgdb/contracts/)

```
KnowledgeNode
├── identity: SystemIdentity {node_id, node_type}     ← obligatorio
├── edges: [Edge {target_id, relation_type, metadata}]
└── facets opcionales (FacetPayload, extra=allow):
    semantics | ast | io_ports | compliance | adr | test_map | git | source
```

- `VocabularyTerm` (node_type, relation_type): token definido por el
  downstream, patrón `^[A-Za-z][A-Za-z0-9_.:-]*$`. kgdb NO impone ontología.
- `GraphSnapshot {version, created_at, nodes, metadata}`: captura completa,
  el contrato de intercambio entre módulos.
- `QueryResult {primary_ids, nodes, metadata}`: envelope de resultados.
- `TransactionManifest` + `PersistenceEntry`: ledger con hash_chain rodante
  para auditoría de mutaciones.

## El pipeline sldb → kgdb (verificado en este repo)

```bash
# 1. Exportar la semántica del store (contrato sldb_kgdb_semantic_export v1)
sldb stores semantic-export --store .sldb --pythonpath . \
  --output /tmp/export.json

# 2. Ingestar a grafo networkx persistido
kgdb ingest-sldb --input /tmp/export.json \
  --output .sldb/runtime/knowledge.nx.json
```

La ingesta (`kgdb.ingest.sldb`) genera nodos con esquema de ids:

| node_type | node_id | edges salientes |
|---|---|---|
| sldb_store | `sldb://store` | has_model → modelos |
| sldb_model | `sldb://model/<Name>` | has_document → docs; tagged_as → tags |
| sldb_document | `sldb://document/<Model>:<name>` | has_section; tagged_as |
| sldb_section | `sldb://section/<id>` | tagged_as |
| sldb_semantic_tag | `sldb://semantic_tag/<tag>` | — |

Todo nodo lleva facet `source` con provenance completa: contrato, productor,
store (root, hash_a), y rutas runtime. La procedencia es reconstruible.

Resultado en este repo: 1000 nodos (1 store + 9 modelos + 274 docs +
~548 secciones + ~168 tags).

## Superficie de consulta (CLI)

```bash
kgdb list  --graph G                    # ids de todos los nodos
kgdb get   --graph G --node <id>        # un nodo completo
kgdb edges --graph G --node <id>        # edges salientes
kgdb query --graph G --query q.json     # StructuredQuery
kgdb ingest --input snap.json --output G       # GraphSnapshot genérico
kgdb ingest-sldb --input exp.json --output G   # export sldb
```

## StructuredQuery (contrato exacto — ojo con los nombres de campo)

```json
{
  "filters":   [ {"facet": "semantics",
                  "conditions": [ {"field": "semantic_tags",
                                   "op": "contains",
                                   "value": "topic:semantic_anchoring"} ] } ],
  "scope":     {"node_id_prefix": "sldb://document/"},
  "relations": [ {"relation_types": ["tagged_as"], "direction": "outgoing"} ]
}
```

- El campo es **`filters`** (no `facet_filters`). Pydantic ignora campos
  desconocidos: una query con el nombre equivocado devuelve TODO el grafo sin
  error. Verificar siempre que el resultado discrimine.
- `facet` ∈ {identity, semantics, ast, compliance, adr, test_map, io}.
- `op` ∈ {eq, ne, is_null, is_not_null, contains, gt, lt, starts_with};
  `contains` es membresía en lista (p.ej. un tag dentro de semantic_tags).
- `scope`: descendant_of | ancestor_of | node_id_prefix (uno solo).
- `relations` filtra qué edges retornan los nodos matcheados, no qué nodos
  matchean.
- Query verificada aquí: tag `topic:semantic_anchoring` → 99 matches de 1000.

## Consulta programática (para bridges)

```python
from kgdb.graph.utils import load_graph          # networkx DiGraph
from kgdb.query.executor import execute_query    # StructuredQuery → [KnowledgeNode]
from kgdb.query.neighborhood import collect_neighborhood
from kgdb.contracts.io import GraphSnapshot      # validación de snapshots
```

## Dos rutas de materialización (no confundir)

1. **`sldb stores semantic-export` + `kgdb ingest-sldb`** — proyección
   fiel del store: modelos, docs, secciones, tags. Es la ruta operativa hoy
   (verificada en este repo).
2. **`deskops graph build`** — extractores propios de deskops que emiten un
   `GraphSnapshot` validado por kgdb (`.sldb/runtime/knowledge_graph.kg.json`).
   Incluye edges declarados en docs; hoy produce 0 edges relacionales aquí
   (ver `atom-a-zero-edge-graph-snapshot-...`).

El kgdb bridge del knowledge core consumirá la ruta 1 para tags/estructura y
necesitará edges autorados (`kgdb.ingest.authored_relations`) para relaciones
tipo `declares_preference`.

## Límites de kgdb (por diseño)

- No hay mutación incremental vía CLI: se re-ingesta el export completo.
- No hay índice semántico propio: los tags son nodos y edges como cualquier otro.
- La frescura es responsabilidad del productor: snapshot viejo = respuestas
  viejas sin warning (por eso el bridge debe comparar hash_a del store).

## Refresh en este repo

```bash
sldb stores semantic-export --store .sldb --pythonpath . --output /tmp/e.json \
  && kgdb ingest-sldb --input /tmp/e.json --output .sldb/runtime/knowledge.nx.json
```

Ejecutar tras cualquier `stores update` que cambie hash_a.
