REFORMULACION
Propósito: en pron, reenlazar el store de deskops como repo hermano `../deskops/.sldb` (hoy `../../../herramientas/deskops/.sldb`) y hacer que su CI clone deskops al lado. Resultado: cuatro archivos modificados —`.sldb/store.yaml`, `.sldb/core/store_index.yaml` (vía CLI sldb), `.github/workflows/check.yml` y `CHANGELOG.md`— con V1-V8 en verde y evidencia en el run dir. Repo: `/mnt/ssd/proyectos/SLDB_1/pron`. Límites: no editar los YAML a mano; no tocar rutas absolutas de modelos, `src/`, Makefile, CI de sldb ni los tests en rojo; no hacer `git add`/commit/push; parar y reportar ante cualquier desvío. Es tarea ejecutable (`task.code`), no agregado.

AMBIGUEDADES
1. "git status --porcelain -- .sldb .github CHANGELOG.md desk no imprime nada". El propio TaskDoc y los `desk/reviews/...` viven bajo `desk/`; si no están en HEAD, p0(a) frena. Obligaría a inventar si están commiteados o si "desk" excluye tasks/reviews.
2. V2 "grep -n 'herramientas' .sldb/store.yaml .sldb/core/store_index.yaml # no imprime nada". El `store_index.yaml` incluido tiene `path: /mnt/ssd/herramientas/sldb/src/sldb/models/rule_doc.py`, que el Scope declara fuera de alcance. V2 fallaría siempre; obligaría a decidir si V2 se limita a la línea deskops.
3. "el target world del Makefile es exactamente:…". El Makefile no está en el bundle (solo en references); obligaría a asumir su contenido.
4. "Si sldb stores add o stores declare cambian … algo más que la línea path … y el campo store_hash". No aclara si `.sldb/core/models/*.yaml` reescritos cuentan como "algo más"; obligaría a decidir.

DRY-RUN
Lecturas: TaskDoc, store.yaml, store_index.yaml, check.yml, CHANGELOG, Makefile. Cambios: `sldb stores add ../deskops/.sldb --name deskops --replace` y `stores declare --write`; paso `deskops next to pron` con `git clone --depth 1 https://github.com/jpcosec/opsys.git ../deskops` tras `Install`; viñeta en `## Sin publicar`. Dependencias: venv `/dev/shm/pron-venv`, CLI sldb, red y deskops hermano. Validaciones futuras: V1-V8 en orden. Nada ejecutado.

FUTURO
Coordinador: commit y push en master de pron y nota a sldb con el hash. sldb: corregir sus rutas absolutas de modelos. Otro nodo: `task-pron-vuelve-a-verde-…` (tests).
