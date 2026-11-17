## REFORMULACION

El nodo es una tarea ejecutable (`task.code`), no un agregado. Propósito: corregir en pron el enlace al store de deskops, que hoy apunta a la ruta de robocop2, y alinear el CI propio. Resultado esperado: `.sldb/store.yaml` y `.sldb/core/store_index.yaml` enlazan `../deskops/.sldb` mediante el CLI de sldb; `.github/workflows/check.yml` clona `jpcosec/opsys` en `../deskops` antes de `make check`; y `CHANGELOG.md` registra el cambio. Repo: `/mnt/ssd/proyectos/SLDB_1/pron`, con deskops como hermano. Límites: no editar a mano los archivos de `.sldb`; no tocar rutas absolutas de modelos de sldb, tests, `src/`, `Makefile`, CI de sldb ni regenerar el mundo; no hacer `git add`, commit ni push; ante cambios distintos de los cuatro archivos previstos, parar y reportar.

## AMBIGUEDADES

1. «make world (o pron docs, V5, si make world pasa) falla con 'No store_index.yaml at'»: obliga a inventar si el control V6 se satisface cuando `make world` pasa y falla `pron docs`, o cuál de los dos comandos es el criterio vinculante.
2. «el target world del Makefile (Makefile:29-32; el ejecutor puede leerlo con sed -n 29,32p Makefile) es exactamente»: obliga a inventar qué hacer si el contenido real del Makefile no coincide con el texto citado: ¿parar, adaptar V4 o confiar en la copia del TaskDoc?
3. «Cualquier otro cambio es un hallazgo: el ejecutor para y lo reporta» frente a «El árbol parte limpio en esas rutas: lo comprueba p0(a)»: p0(a) solo inspecciona `.sldb`, `.github`, `CHANGELOG.md` y `desk`, mientras V8 mira todo salvo `runs`; obliga a inventar si suciedad preexistente fuera de esas rutas bloquea la ejecución.

## DRY-RUN

Lecturas: TaskDoc, rituales, `store.yaml`, `store_index.yaml`, `check.yml`, `CHANGELOG.md` y `Makefile:29-32`. Cambios previstos: ejecutar `sldb stores add ../deskops/.sldb --name deskops --replace` y `sldb stores declare --write`; añadir el paso de clonado entre `Install` y `check`; añadir una viñeta en `## Sin publicar`. Dependencias: venv `/dev/shm/pron-venv`, sldb CLI, deskops hermano y red para los clones de V4/V6. Validaciones futuras: V1-V8, con V4/V6 en copias temporales y control con los archivos de `HEAD`. No se ejecuta nada.

## FUTURO

El coordinador revisa la evidencia, commitea y pushea en `master` de pron, y envía a sldb la nota con el hash. Las fallas de tests de pron y las rutas absolutas de modelos de sldb quedan fuera y las atienden otras tareas o sldb.
