## REFORMULACION

**Propósito:** que JP elija, entre A/B/C, si pron versiona `.sldb/` o queda como excepción al layout de sldb c420809c, y dejarlo escrito.

**Resultado:** `docs/decision-store-sldb.md` con una línea exacta `Opción elegida: X`, fecha del dispose, razón de JP y consecuencias; commit y push a master; si A o B, una `task.code` que implemente, sin implementarla.

**Repo:** `/mnt/ssd/proyectos/SLDB_1/pron`, master.

**Límites:** no elegir por JP; no editar `.gitignore`, `Makefile` ni `src/pron`; no cambiar sldb; no correr `sldb stores migrate-layout`; si el recibo owner sigue `pending`, parar sin escribir.

## AMBIGUEDADES

1. “si sigue pending, parar sin escribir nada: JP lo dispone con … `--reason 'Opción <letra>: <razón>'`”. El ejecutor no puede producir la letra ni la razón; obligaría a inventar quién ejecuta ese dispose.
2. “la razón copiada del reason de JP”. Si el reason no respeta `Opción <letra>: <razón>`, no se define qué copiar ni cómo extraer la letra.
3. “las consecuencias de esa opción para sldb stores check y para los recibos del desk, tomadas del goal”. El goal solo detalla consecuencias para C; para A y B obligaría a inventarlas.
4. “owner accepted e intact”. “Intact” no tiene criterio verificable.
5. “un solo commit con docs/decision-store-sldb.md y los archivos de desk/ que deskops haya tocado”. No se enumeran; podría incluir recibos no versionados.
6. “mensaje con [skip ci]”. No hay mensaje exacto.
7. “--goal, --scope y --validation derivados de la opción”. El contenido queda indeterminado.

## DRY-RUN

**Lecturas:** task file, nota del inbox, `.gitignore`, `Makefile`, salida de `deskops review status …`, `git status`.
**Cambios previstos:** crear `docs/decision-store-sldb.md`; si A/B, `deskops add task` (escribe `desk/tasks`); commit y `push origin master`.
**Dependencias:** dispose de JP con verdict `accepted`; `deskops`; git; red/origin.
**Validaciones futuras:** `grep -nE '^Opción elegida: [ABC]$'`; review status accepted; `git log -1 --format=%H -- docs/decision-store-sldb.md`.

## FUTURO

JP dispone el recibo owner con letra y razón; `deskops add task` materializa la `task.code`; un ejecutor posterior implementa A/B; el push y CI validan.
