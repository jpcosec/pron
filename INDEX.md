# Índice del repo

Árbol versionado a nivel 2. Para qué es pron y cómo funciona, ver [`README.md`](README.md); para lo que debería ser, [`source/spec/README.md`](source/spec/README.md).

```
.
├── README.md             generado por `pron docs` desde knowledge/readme.md y knowledge/explanations/
├── INDEX.md              este índice
├── CHANGELOG.md          versiones tageadas
├── pyproject.toml        paquete `pron`; extra `dev` (pytest, syrupy, ruff, mypy)
├── Makefile              check · lint · audit · test · world · docs-check
├── constraints.txt       commits de sldb y kgdb contra los que se prueba (la CI lo lee acá)
├── .github/workflows/    CI: `make check`
│
├── src/pron/             el código, por eje
│   ├── kernel/           primitivas: parts/ (datos del turno), sexp/ (lector de formas), actions/ (verbos de acción), el Kernel
│   ├── world/            el mundo desde sldb: World, Store, Graph, Lexicon, matching/
│   ├── surface/          lenguaje natural → formas
│   ├── sexpr/            formas ↔ sldb/kgdb: turn/ forms/ resolving/ planning/ prevalidation/ execution/ dialogue/
│   ├── cli/              `pron`, un comando por archivo en commands/
│   ├── remote/           cliente del daemon (`pron serve`), solo biblioteca estándar
│   ├── corpus/  models/  índice de oraciones; modelos de documento de pron
│   └── session.py …      el turno (Session), serve, docs, lints
├── tests/                en espejo del código: world/ sexpr/ session/ cli/ remote/ corpus/
│   ├── golden/           red de caracterización (syrupy): respuesta, trace, record y CLI por guion
│   └── worlds/           mundos de prueba (el restaurante del spec 09a, valores)
│
├── source/spec/          la especificación, en capítulos (01-mundo … 13-formas)
├── knowledge/            lo que se escribe del mundo de pron: explanations/, anchors/, projections/, readme.md
├── ledger/               MoveDoc de los turnos dichos sobre este mundo
│
├── docs/                 documentación para personas
│   ├── spec2viz/         diagramas: specs/*.yml → `python build.py` → index.html, offline.html
│   └── HANDOFF.md        traspaso entre sesiones (2026-09-09, histórico)
└── tools/                herramientas de desarrollo: check_file_length.py (`make audit`), merkle_bench.py
```

## Lo que no está en git

Todo lo derivado se reconstruye, no se versiona (ver `.gitignore`):

- `.sldb/` (el store de sldb), `kgdb/` y `knowledge/{surfaces,commands,relations}/` (lo que generan `pron init --knowledge` y `pron docs`): `make world`.
- `docs/spec2viz/out/`, sus HTML y `diagrams.md`: `python docs/spec2viz/build.py`.
- `.pron/` (grafo y vectores), caches de Python, pytest, ruff y mypy.
