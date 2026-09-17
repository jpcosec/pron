# Índice del repo

Árbol a nivel 2, generado a mano a partir de `find . -maxdepth 2` (se excluyen `.git`, `.mypy_cache`, `.pytest_cache`, `.ruff_cache` y `__pycache__`). Para el "por qué" de cada capa, ver [`README.md`](README.md); para el "qué debería ser", [`source/spec/README.md`](source/spec/README.md).

```
.
├── bench/                  benchmarks (merkle.py)
├── CHANGELOG.md            historial de versiones tageadas
├── constraints.txt         versiones fijadas de sldb/kgdb consumidas por pron
├── HANDOFF.md              estado de traspaso entre sesiones (pron, sldb, kgdb, legos)
├── kgdb/
│   └── relation_types/     RelationTypeDoc de este mundo (applies_to_*, extends, has_*, names, semantic_*, tagged_as)
├── .knowledge/             vacío, no trackeado — no confundir con knowledge/
├── knowledge/              la KB de pron sobre sí mismo, generada por `pron docs` (no se edita a mano)
│   ├── anchors/            AnchorDoc — alias que no calzan con modelo, campo o tag
│   ├── commands/           CliCommandDoc — un doc por comando de la CLI
│   ├── explanations/       ExplanationDoc
│   ├── projections/        ProjectionDoc — qué puede nombrar una sesión
│   ├── relations/          aristas `implements`: módulo → capítulo de source/spec que cita
│   ├── surfaces/           SurfaceDoc — superficie de cada símbolo del código
│   └── readme.md
├── ledger/                 MoveDoc por turno (interpretación, consultas, escritura, hash_mundo antes/después)
├── Makefile                make check | test | format | lint | typecheck | docs-check
├── .pron/                  derivado, fuera de git — grafo tipado (graph.nx.json) y vectores de este store
├── pyproject.toml          paquete `pron`, extras `dev`
├── README.md               qué es pron, cómo probarlo y usarlo, capas de src/pron
├── .sldb/
│   ├── core/               store de sldb de este repo — documents/, models/, sections/, semantic/, store_index.yaml
│   └── runtime/            cache/ y locks/ derivados (cache excluida de git)
├── source/
│   └── spec/               especificación en 13 capítulos (01-mundo … 13-formas) + 09a (mundo del restaurante, fixture de aceptación)
├── src/
│   ├── pron/               paquete: world, store, graph, lexicon, embedder, surface/, resolve, verbs, kernel, dialogue, ledger, session, client, cli/, models/, docs, forms, response, display, refs, ids, sexp, corpus
│   └── pron.egg-info/      metadata de instalación editable
├── tests/                  ~25 archivos test_NN_*.py numerados por capítulo/feature + worlds/ (fixtures: restaurant.py)
└── views/
    └── spec2viz/           diagramas semánticos (YAML) → Mermaid/SVG → catálogo HTML; ver views/spec2viz/README.md
```

## Notas

- `knowledge/` y `.sldb/core/` son las dos caras de lo mismo: `.sldb/core/documents` guarda los documentos crudos que `pron docs` genera y sldb indexa; `knowledge/` es su proyección legible en markdown por tipo de modelo. Ninguno de los dos se edita a mano — se regeneran con `pron docs --world . --pythonpath .`.
- `.knowledge/` (con punto, vacío) es un directorio suelto sin historial en git; no es parte del flujo de documentación y puede limpiarse con seguridad si estorba.
- `source/spec/` es la especificación (el objetivo); `src/pron/` es la implementación; `views/spec2viz/` es la proyección gráfica de ambas — `target.*.yml` documenta el objetivo de source/spec, `codigo.capas.yml` documenta las capas reales de src/pron (tabla "Capas" de README.md).
- La v1 completa (código, KB y store viejos) vive en la rama `v1-code-and-kb` / tag `v1-frozen`, no en este árbol.
