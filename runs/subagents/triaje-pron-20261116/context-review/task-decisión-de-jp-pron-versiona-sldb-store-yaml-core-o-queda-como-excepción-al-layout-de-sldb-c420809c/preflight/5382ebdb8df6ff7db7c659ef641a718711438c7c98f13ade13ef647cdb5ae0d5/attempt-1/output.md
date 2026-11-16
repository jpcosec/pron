## REFORMULACION

**Propósito:** registrar y commitear en pron la decisión de JP sobre si `.sldb/` (store.yaml + core/) se versiona, dado que pron ignora `.sldb/` entero (`.gitignore` línea 10) y `make world` (Makefile 29-32) regenera ~740 documentos derivados; esto rompe `sldb stores check` (`stores/core_ignored`), declara el desk roto y hace que los recibos no viajen en un clon.

**Resultado:** `docs/decision-store-sldb.md` commiteado y pusheado con "Opción elegida: A|B|C", recibo owner accepted y, si A o B, una `task.code` referenciada.

**Repo:** pron (`/mnt/ssd/proyectos/SLDB_1/pron`), master.

**Límites:** no editar `.gitignore`/Makefile/`src/pron`, no cambiar sldb, no correr `stores migrate-layout`; solo documenta y delega la implementación.

Es un nodo de decisión (`task.decision`), no ejecutable por el agente sin veredicto humano; no es un agregado.

## AMBIGUEDADES

1. "JP elige una de tres opciones" frente a "Recomendación del coordinador: A": ¿el ejecutor adopta A o espera? Obligaría a inventar la autoría de la elección.
2. "dispone el recibo owner ya registrado": no consta que exista ni su identificador; obligaría a inventar que está registrado.
3. "commit ... y push a origin master": no se autoriza explícitamente el push; obligaría a asumir permiso y rama.
4. "deskops add task --root . --task-type task.code": sintaxis no verificable en el input; obligaría a inventar flags.
5. "'Opción elegida: A|B|C'": ¿literal con pipes o valor concreto? Obligaría a elegir formato frente al grep regex.

## DRY-RUN

**Lecturas:** TaskDoc, inbox `20261104-233659`, `.gitignore:10`, `Makefile:29-32`, docs existentes, estado del recibo owner.
**Cambios previstos:** crear `docs/decision-store-sldb.md`; opcionalmente `task.code`; commit `[skip ci]` y push.
**Dependencias:** veredicto JP (owner accepted), deskops operativo, remote origin/master.
**Validaciones futuras:** `test -f` + grep regex; `deskops review status`; `git log -1` alcanzable desde HEAD.

## FUTURO

JP elige A/B/C y redacta la razón; confirma si el recibo owner ya está registrado; autoriza el push; si A/B, otro nodo implementa `.gitignore`/Makefile/src, y `sldb stores migrate-layout` queda fuera.
