REFORMULACION
Propósito: que el enlace del store deskops en pron resuelva como repo hermano `../deskops/.sldb` en robocop2, en el layout del CI de sldb y en el CI propio de pron. Resultado: `.sldb/store.yaml` y `.sldb/core/store_index.yaml` con esa ruta (vía CLI sldb, no a mano); paso nuevo en `.github/workflows/check.yml` entre `Install` y `check (lints + typecheck + tests + docs)` que clona `jpcosec/opsys` en `../deskops`; viñeta en `CHANGELOG.md`; V1–V8 con evidencia en el run dir. Repo: `/mnt/ssd/proyectos/SLDB_1/pron` (robocop2). Límites: no tocar rutas absolutas de modelos de sldb, `src/`, `Makefile`, CI de sldb ni tests; no regenerar el mundo en el checkout real; no `git add/commit/push`; si `stores add/declare` cambia algo más que la línea path y `store_hash`, parar y reportar.

AMBIGUEDADES
1. V2: "grep -n 'herramientas' .sldb/store.yaml .sldb/core/store_index.yaml # no imprime nada" frente a Scope: "las rutas absolutas de modelos de paquete de sldb ... 'path: /mnt/ssd/herramientas/sldb/...' ... no entra". Si esas líneas permanecen, V2 imprime y falla; obligaría a inventar si acotar el grep a `herramientas/deskops` o eliminar rutas fuera de alcance.
2. CHANGELOG: "viñeta al final de la lista bajo '## Sin publicar'". Si esa sección no existe, obliga a inventar su ubicación.

DRY-RUN
Sin ejecutar. Lecturas: `.sldb/store.yaml`, `.sldb/core/store_index.yaml`, `check.yml`, `CHANGELOG.md`, `Makefile` y `git status` de esas rutas. Cambios previstos: p0 comprueba árbol limpio y venv; p1 ejecuta `sldb stores add ../deskops/.sldb --name deskops --replace` y `stores declare --write`; p2 inserta el paso de clone; p3 añade la viñeta. Dependencias: venv `/dev/shm/pron-venv` (o recrearlo con `uv`), CLI sldb, red para clonar `jpcosec/opsys` en V4/V6, `TMPDIR=/dev/shm`. Validaciones futuras: V1 `stores list`, V2 grep, V3 `linked_store`, V4 `make world` en layout CI, V5 `pron docs`, V6 control con archivos de HEAD, V7 orden de pasos, V8 diff acotado a cuatro archivos.

FUTURO
El coordinador hace commit y push en master de pron y manda nota a sldb con el hash; sldb atiende las rutas absolutas de modelos; las fallas de tests quedan en `task-pron-vuelve-a-verde`.
