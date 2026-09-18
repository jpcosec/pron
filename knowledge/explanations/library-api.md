# Como librería para un runtime

## Question

¿Cómo se usa pron como librería?

## Answer

Un runtime que ya tiene su propio parser (un LLM, por ejemplo) no necesita la superficie de pron, pero sí lo que hay debajo, para no armar su propio grafo ni su propio índice:

- `World(root, pythonpath)`: abre el mundo; `refresh()` pone al día el índice de aristas de sldb (`stores update` + `sldb.api.rebuild_edges`, por librería) y `refresh_if_stale()` solo cuando sldb reporta un documento cuyo shard está ausente o desactualizado (una escritura hecha por fuera de sldb); `derived_dir` es `.pron/`, fuera de git, para lo que el consumidor derive.
- `World.store` (`Store`): la única puerta a sldb: documentos cacheados, `find(scope, where)`, `matches`, `schema`, y escrituras con roundtrip (`create`, `update_field`, `append`, `untrack`).
- `World.graph` (`Graph`): compone el índice de aristas de sldb en cada lectura, sin persistir nada propio ni depender de networkx. Además de `edges_from`/`edges_to`: `nodes_of_type`, `targets`/`sources`, `roots(node_type, relation)`, `children`/`parent`/`descendants` (por defecto sobre `semantic_parent`) y `neighbors_via(node, relation, exclude_prefixes=...)` para hermanos por tag. Todo parametrizado por nombre de relación; pron no sabe cuáles declara un mundo.
- `DocumentIndex(Matcher(embedder), cache_path)`: documentos rankeados por similitud. `index([(key, hash, text)])` embebe solo lo que cambió y persiste los vectores en un archivo derivado; `rank(query, k, threshold)` devuelve `[(key, score)]`. Sin embedder rankea con difflib y el archivo lo dice.

## Sources

- SpecDoc:spec-12
