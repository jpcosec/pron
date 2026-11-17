## REFORMULACION

**Propósito:** corregir en pron el enlace del store de deskops para que resuelva como repo hermano `../deskops/.sldb`, no por la ruta de robocop2 `../../../herramientas/deskops/.sldb`, y hacer que el CI propio de pron clone deskops al lado antes de `make check`.

**Resultado:** `.sldb/store.yaml` y `.sldb/core/store_index.yaml` con el nuevo `path` (vía CLI `sldb`, sin edición manual); paso `deskops next to pron` en `.github/workflows/check.yml` que clona `jpcosec/opsys` en `../deskops`; viñeta en `CHANGELOG.md`; V1–V8 verdes y solo esos cuatro archivos modificados.

**Repo:** pron en `/mnt/ssd/proyectos/SLDB_1/pron`; deskops como checkout hermano.

**Límites:** no tocar rutas absolutas de modelos, tests fallidos, `src/`, `Makefile`, CI de sldb, ni hacer git add/commit/push. Ante desvío, parar y reportar. Nodo ejecutable, no agregado.

## AMBIGUEDADES

1. «jpcosec/opsys (repo público de deskops)»: no aclara la relación entre `opsys` y `deskops` ni si ese es el remote canónico; obligaría a asumir que `opsys` es deskops.
2. «el ejecutor para y lo reporta»: no indica destino ni canal del reporte; obligaría a inventar run dir, stdout o nota.
3. «la sección en la línea 3; la siguiente, '## 1.0.0 — 2026-09-10', está en la línea 19»: ancla por número de línea; obligaría a asumir que el CHANGELOG no cambió.
4. «algo más que la línea path del enlace deskops y el campo store_hash de store_index.yaml»: no define otros cambios tolerables (orden, formato); obligaría a fijar un umbral de desvío.

## DRY-RUN

**Lecturas:** TaskDoc y referencias; `.sldb/store.yaml`, `.sldb/core/store_index.yaml`, `.github/workflows/check.yml`, `Makefile:29-32`, `CHANGELOG.md`; `git status --porcelain`.

**Cambios previstos:** p0 comprueba árbol limpio y venv; p1 ejecuta `sldb stores add` y `stores declare` (solo dos archivos); p2 inserta el paso YAML tras `Install`; p3 añade la viñeta; p4 corre validaciones y guarda evidencia.

**Dependencias:** uv/Python 3.12, CLI `sldb`, red para clonar `jpcosec/opsys`, espacio en `/dev/shm`, hasta ~40 min.

**Validaciones futuras:** V1–V8, incluido control negativo V6 y `git diff` acotado.

## FUTURO

Coordinador: commit/push en master y nota a sldb con el hash. sldb: rutas absolutas de modelos (nota aparte). Otra tarea: goldens `test_16`, `test_04`, `test_10`. Humano: decidir ejecución en segundo plano de V4/V6.
