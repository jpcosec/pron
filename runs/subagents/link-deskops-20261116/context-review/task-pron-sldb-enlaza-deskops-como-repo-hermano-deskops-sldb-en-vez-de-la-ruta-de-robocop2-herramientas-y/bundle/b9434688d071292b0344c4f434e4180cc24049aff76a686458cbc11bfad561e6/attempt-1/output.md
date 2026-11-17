## REFORMULACION

Propósito: corregir en `pron` el enlace al store de deskops y hacer que su CI tenga deskops al lado. Resultado: `../deskops/.sldb` en `.sldb/store.yaml` y `.sldb/core/store_index.yaml` mediante el CLI de sldb; paso de clonado en `.github/workflows/check.yml`; viñeta en `CHANGELOG.md`; V1-V8 con evidencia. Repo: `/mnt/ssd/proyectos/SLDB_1/pron`. Límites: solo esos cuatro archivos; no editar los YAML a mano; no tocar tests, `src/`, Makefile, CI de sldb ni rutas absolutas de modelos; no hacer `git add`, commit ni push; parar y reportar ante cambios extra. Es una tarea de código ejecutable, no un agregado.

## AMBIGUEDADES

1. Cita: “si falta, el ejecutor lo recrea”. Solo cubre el venv ausente; si existe pero está incompleto, con otro Python o sin sldb editable, no dice si reusarlo, repararlo o recrearlo. Obligaría a inventar una política.
2. Cita: “# imprime 'deskops -> ../deskops/.sldb'”. Fija un formato exacto para `sldb stores list`; si imprime columnas extra o una ruta absoluta, no aclara si V1 pasa. Obligaría a inventar el criterio de aceptación.
3. Cita: “son las tres líneas del target world del Makefile”. El Makefile no está entre los archivos del input, así que la afirmación de que `make world` no corre tests no es verificable aquí. Obligaría a confiar en contenido no mostrado o a inspeccionarlo.

## DRY-RUN

Lecturas: TaskDoc, rituales, `.sldb/store.yaml`, `.sldb/core/store_index.yaml`, `.github/workflows/check.yml`, `CHANGELOG.md`; pills y átomos vacíos no añaden pasos. Cambios previstos: ejecutar `sldb stores add ../deskops/.sldb --name deskops --replace` y `sldb stores declare --write`; comprobar que el diff solo toca la línea `path` y `store_hash`; insertar el paso `deskops next to pron` entre `Install` y `check`; añadir la viñeta. Dependencias: venv/uv, red para clonar `jpcosec/opsys`, espacio en `/dev/shm`, sldb main y deskops hermano. Validaciones futuras: V1-V8 en orden, con V4/V6 largos y evidencia en el run dir; detenerse ante cualquier cambio extra.

## FUTURO

El coordinador commitea y pushea `master`, y manda la nota a sldb con el hash. Los CI de pron y de sldb validan tras el push. JP o el coordinador deciden hallazgos y cierre; el ejecutor no indexa, no publica y no regenera el mundo real.
