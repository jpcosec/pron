PASS

# Resultado del tester deskops-t-5c0748a304c0 (pron, versionar .sldb/)

Fecha 2026-11-16, master en d94a3a1, árbol de trabajo sin indexar. La evidencia completa está en `test.log`, en este mismo run dir.

## 1. El diff cumple el contrato: PASS
- `.gitignore`: el numstat da `1 2`. Se borró solo la línea `.sldb/`, que ya no aparece (`grep -nxF '.sldb/'` sale con rc 1). El comentario de la línea 9 se reescribió y coincide al pie de la letra con el texto del Implementation Path (`grep -nxF` lo encuentra en 9:).
- `sldb/` sigue en la línea 10 y `.sldb_cache/` sigue en la 25. Las dos líneas no cambiaron; solo bajaron un número al quitarse `.sldb/`.
- `CHANGELOG.md`: el numstat da `1 0`. La viñeta es exacta (`grep -cxF -e` da 1) y es la última de `## Sin publicar`: el awk devuelve esa viñeta como último ítem, seguida de una línea en blanco y de `## 1.0.0`.

## 2. Las seis comprobaciones de Validation, en orden: PASS
- V1 `git branch --show-current` imprime `master`.
- V2 `check-ignore .sldb/store.yaml; test $? -eq 1` sale con rc 0.
- V3 `check-ignore .sldb/core/store_index.yaml; test $? -eq 1` sale con rc 0.
- V4 `check-ignore .sldb_cache; test $? -eq 0` sale con rc 0.
- V5 `stores check | grep -cE 'stores/(core_ignored|cache_not_ignored)'` imprime `0` (el rc 1 de grep es el esperado).
- V6 da status=817 y find=817, iguales, con rc 0. Las 817 entradas son `??`: ninguna fila tiene otro estado.

## 3. No se versiona nada runtime: PASS
- `find .sldb -maxdepth 2` encuentra solo `store.yaml` y `core/`; dentro de `core/` están `store_index.yaml`, `models/` y `documents/`.
- `.sldb_cache` aparece 0 veces en `git status --porcelain --untracked-files=all`.
- No hay locks, `*.tmp`, `*.pid`, sqlite, db ni pickle, ni directorios `runtime/`, `edges/`, `sections/`, `semantic/`, `graphs/` o `cache/`. Los 817 archivos son `.yaml` y suman 3,5 MB. Lo que hay bajo `documents/` son directorios por modelo (TaskCodeDoc, ReviewDoc, InboxNoteDoc, …).
- Nota informativa, no es un fallo: el Rationale midió 789 archivos y 3,3 MB; hoy son 817 y 3,5 MB. La diferencia son documentos del desk escritos después de esa medición, y todos son yaml de `core/`.

## 4. No cambió nada más: PASS
Fuera de `desk/`, `runs/`, `.deskops.log` y `.sldb/`, `git status --short` muestra solo ` M .gitignore` y ` M CHANGELOG.md`.

## 5. El store se lee bien: PASS
`TMPDIR=/dev/shm sldb stores check --pythonpath .` sale con rc 1 y reporta 7 errores y 30 alertas:
- los 7 errores son `store/model-unresolved`, en AnchorDoc, ProjectionDoc, MoveDoc, TheoremDoc, SpecDoc, ExplanationDoc y ReadmeDoc. Están fuera de scope según la TaskDoc;
- `[stores/` aparece 0 veces;
- las alertas son 26 `anchors/doc_lost` y 4 `anchors/doc_changed`, en anclas de ReviewDoc. Son alertas, no errores, y no son `stores/*`.

Incidencia del propio test: en C1, el primer `grep -cxF` falló con rc 2 porque el patrón empieza con `-`. Se repitió con `-e` al final de `test.log` y pasó.
