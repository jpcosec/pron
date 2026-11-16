## REFORMULACION

**Propósito:** registrar y dejar commiteada en pron la decisión de JP sobre si `.sldb/` (store.yaml + core/) se versiona, eligiendo entre A (versionar todo), B (separar stores) o C (excepción declarada).

**Resultado:** `docs/decision-store-sldb.md` con la opción, fecha, razón y consecuencias; recibo owner accepted; si A/B, una `task.code` en desk/tasks que la implemente y referencie el documento.

**Repo:** pron (`/mnt/ssd/proyectos/SLDB_1/pron`), rama master.

**Límites:** no cambia sldb, no edita `.gitignore`, `Makefile` ni `src/pron`, no ejecuta `sldb stores migrate-layout`; si A/B solo crea la task.code, no la implementa.

## AMBIGUEDADES

1. "deskops add task --root . --task-type task.code con la implementación" — no fija título ni id; obligaría a inventar el identificador y el alcance exacto de esa task.code.
2. "el recibo owner ya registrado con deskops review dispose 'review-…-owner-1' --verdict accepted" — el input no incluye ese recibo ni confirma que exista; obligaría a asumir su presencia y su id exacto.
3. "commit de docs/decision-store-sldb.md y del desk con [skip ci]" — no dice si es un commit o varios; obliga a inventar la granularidad.
4. "escribir docs/decision-store-sldb.md con la línea 'Opción elegida: A|B|C', fecha, razón y consecuencias" — "fecha" no se define (decisión de JP vs. de ejecución).
5. Validación `grep -nE 'Opción elegida: (A|B|C)'` — el patrón admite texto literal `A|B|C`; no exige una sola letra. Obliga a inventar el formato canónico.

## DRY-RUN

**Lecturas:** nota de inbox, `.gitignore`, `Makefile`, rituales enrutados, `pills`/`atoms` (vacíos), recibo owner si existe.
**Cambios previstos:** crear `docs/decision-store-sldb.md`; si A/B, crear una `task.code` en desk/tasks; commit con `[skip ci]` y push a origin master.
**Dependencias:** elección de JP, CLI `deskops`, acceso a git/origin, recibo owner disponible.
**Validaciones futuras:** las tres del TaskDoc (existencia+grep del documento, `review status` del recibo, `git log -1` alcanzable desde HEAD).

Es tarea única (no agregado); su ritual es execution, aunque depende de una decisión humana previa.

## FUTURO

JP elige A/B/C y dispone el recibo; `deskops` produce/actualiza la task.code; un nodo implementador posterior ejecuta A o B; un humano valida el commit y el cierre del desk.
