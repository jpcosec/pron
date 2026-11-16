## REFORMULACION
Encargo ejecutable (`task.code`) en el repo pron: migrar `docs/spec2viz/build.py` de spec2viz a specir (tres `run()` de líneas 22-24), actualizar docstrings, README (líneas 14, 20-25), entrecomillar dos `label` en `specs/target.components.yml` (121, 128), cambiar `-w` por `--size` en la llamada a mmdc (línea 46) y añadir viñeta en CHANGELOG. Instalar specir como herramienta uv (p1), validar con los tres comandos de Validation, commit en master + push (p5) y aviso a IR con el hash (p6). Límites: no renombrar directorio/specs, no commitear salidas generadas, no tocar IR/spec2viz/sldb, no desinstalar spec2viz, no cambiar la línea 5 del README ni `.gitignore`.

## AMBIGUEDADES
1. "cambiar solo el primer argumento 'spec2viz' por 'specir' en las tres llamadas" — pero el `build.py` del bundle ya muestra `run('specir', ...)` y docstrings ya en specIR; obligaría a inventar si el ejecutor reaplica, verifica o considera no-op.
2. "docs/spec2viz/README.md ... reemplazar el comando spec2viz por specir" — el README del bundle ya dice `specir`; misma indeterminación.
3. "agregar en CHANGELOG.md ... '- docs/spec2viz/build.py valida...'" — la viñeta ya existe en el bundle; obligaría a decidir si duplicar o saltar.
4. "commit de build.py, README.md y CHANGELOG.md en master" — omite `specs/target.components.yml`, que p3b modifica; obligaría a inventar si incluirlo.
5. "las líneas citadas son las de master al crear la tarea" — sin acceso a master no se puede confirmar correspondencia; obligaría a asumir el estado del bundle como master.

## DRY-RUN
Lecturas: `build.py`, `README.md`, `specs/target.components.yml`, `CHANGELOG.md`, TaskDoc y rituales. Comprobaciones: `uv tool install --reinstall --editable /mnt/ssd/proyectos/SLDB_1/IR --with-editable /home/robocop/herramientas/sldb`; tres `--help` con rc 0. Cambios previstos: sustituir comandos en `run()`, docstrings, README, entrecomillar labels 121/128, `-w`→`--size`, viñeta CHANGELOG. Dependencias: uv, mmdc en PATH (`/mnt/ssd/herramientas/mermaid-cli`), `.venv/bin/specir` en IR. Validaciones futuras: grep sin salida; `build.py` rc 0 imprimiendo "Generated 4 SVGs..."; `specir retirement check` sin fila `pron`. Luego commit/push y `deskops message send`. Nada se ejecuta aquí.

## FUTURO
Un humano/otro nodo decide el estado real de master, resuelve la contradicción del commit (punto 4), ejecuta p1-p6 y envía el mensaje a IR; IR actualiza su acta de retiro.
