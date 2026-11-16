## REFORMULACION
Encargo: que JP elija entre A/B/C sobre versionar `.sldb/` en pron y dejar la decisión registrada. Resultado: `docs/decision-store-sldb.md` con `Opción elegida: X`, fecha del dispose, razón y consecuencias; commit y push; si A o B, crear una `task.code` que implemente. Repo: `/mnt/ssd/proyectos/SLDB_1/pron`. Límites: el ejecutor no elige ni adopta la recomendación, no implementa A/B, no toca `.gitignore`, `Makefile`, `src/pron` ni sldb, y no corre `stores migrate-layout`. Es una tarea `task.decision`, no un agregado ejecutable.

## AMBIGUEDADES
1. «la letra elegida se lee de ese reason»: obliga a inventar un parser si el `reason` no respeta `Opción <letra>: <razón>`.
2. «campo disposed_at del recibo, formato AAAA-MM-DD»: obliga a inventar conversión si el recibo guarda timestamp ISO.
3. «las consecuencias de esa opción [...] tomadas del goal»: el goal no da texto literal por opción; obliga a inventar redacción.
4. «los archivos de desk/ que deskops haya tocado»: no se declara qué escribe `review dispose`; obliga a inventar el alcance del commit.
5. «push a origin master»: no se declara la rama actual; obliga a inventar si no es `master`.
6. «--goal, --scope y --validation derivados de la opción»: obliga a inventar contenido de la `task.code`.

## DRY-RUN
Lecturas: TaskDoc, rituales, `.gitignore`, `Makefile`, `docs/` existente y `deskops review status`. Cambios previstos: crear `docs/decision-store-sldb.md`; opcionalmente `desk/tasks/task.code`; un commit y push. Dependencias: recibo owner `accepted`, dispose de JP con `reason`, CLI `deskops`. Validaciones futuras: `grep` de la línea exacta, `review status`, `git log` alcanzable.

## FUTURO
JP dispone verdicto y razón; `deskops` registra el recibo; un ejecutor posterior implementa A/B si aplica; un humano o CI confirma el push.
