## REFORMULACION

Encargo ejecutable (task.code) en el repo pron, raíz `/mnt/ssd/proyectos/SLDB_1/pron`. Propósito: que el enlace del store deskops deje de apuntar a la ruta de robocop2 y resuelva como repo hermano. Resultado esperado: (a) enlace `../deskops/.sldb` en `.sldb/store.yaml` y `.sldb/core/store_index.yaml`, hecho con el CLI de sldb (nunca editando YAML a mano); (b) paso nuevo en `.github/workflows/check.yml`, entre `Install` y el paso de check, que clone `jpcosec/opsys` en `../deskops`; (c) viñeta en `CHANGELOG.md` bajo `## Sin publicar`. Límites: no tocar `src/`, `Makefile`, CI de sldb, tests, rutas absolutas de modelos de paquete, ni hacer git add/commit/push; ante cualquier desvío, parar y responder `BLOQUEADO: <motivo>` dejando evidencia. Cierre del ejecutor: V1–V8 verdes y solo esos cuatro archivos modificados.

## AMBIGUEDADES

1. "en result-summary.md del run dir que da el brief del coordinador" — el input no incluye esa ruta; obliga a inventar el run dir.
2. "un paso nuevo entre 'Install' y 'check (lints + typecheck + tests + docs)'" — asume nombre literal del paso; V7 solo exige `startswith('check')`, así que el nombre real es incierto.
3. "correrlo con timeout de 40 min o en segundo plano" — dos alternativas sin criterio de elección.
4. "una viñeta al final de la lista de viñetas bajo '## Sin publicar'… justo antes del encabezado '## 1.0.0 — 2026-09-10'" — si la sección tuviera subsecciones u otra estructura, hay que decidir el punto de inserción.
5. Metadatos plantilla "summary: ''" y "_Explain why this task exists or the business driver behind it._" — no son instrucciones ejecutables; indefinido si deben rellenarse.

## DRY-RUN

Lecturas: `git status --porcelain -- . ':!runs'` (p0a), comprobación del venv (p0b), `sed -n 29,32p Makefile`, y los cuatro archivos de Files. Cambios previstos: dos comandos `sldb stores add … --replace` y `sldb stores declare --write`; inserción de un paso YAML en check.yml; una viñeta en CHANGELOG.md. Dependencias: venv `/dev/shm/pron-venv`, red para clonar `jpcosec/opsys`, `rsync`, `git`. Validaciones futuras (no ejecutadas): V1 lista de stores, V2 grep sin coincidencias, V3 `linked_store`, V4/V5 `make world` y `docs` en layout CI, V6 control con archivos de HEAD, V7 orden de pasos, V8 `git diff` acotado.

## FUTURO

Tras el closeout, el coordinador commitea y pushea en master y envía nota a sldb con el hash; también remite a sldb la nota aparte sobre rutas absolutas de modelos. Un humano decide si un desvío en p0/V8 bloquea o reencuadra la tarea.
