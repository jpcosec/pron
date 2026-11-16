REFORMULACION
Propósito: migrar la única dependencia de spec2viz en pron a specir, pedido IR13/gate G4. Resultado: `docs/spec2viz/build.py` invoca `specir diagram validate`, `diagram render` y `catalog build` con los mismos argumentos; `python3 docs/spec2viz/build.py` sale rc 0; README y CHANGELOG quedan coherentes; commit en master pusheado y mensaje a IR con el hash. Repo: pron. Límites: solo build.py (tres `run()` y docstrings), README (frase y bloque de comandos), CHANGELOG, instalación local de specir y respuesta a IR. No renombrar `docs/spec2viz`, no commitear salidas generadas, no tocar IR/spec2viz/sldb, no desinstalar spec2viz ni decidir el `.gitignore` de `.sldb/`. Tarea ejecutable, no agregado.

AMBIGUEDADES
ninguna.

DRY-RUN
Lecturas: TaskDoc, nota de inbox, `correspondencia-cli.md`, `acta-de-retiro.md`, `build.py`, `README`, `CHANGELOG` y, si hace falta, `.gitignore`. Cambios previstos: instalar specir con `uv tool install --reinstall --editable ...` en la máquina; cambiar los tres `run('spec2viz', ...)` por `run('specir', ...)` y los dos docstrings; en README sustituir por texto, no por número de línea; añadir la viñeta en CHANGELOG. Dependencias: uv, checkouts editables de IR y sldb, mmdc, PyYAML, `.venv/bin/specir`, git y deskops. Validaciones futuras: `grep` sin `run('spec2viz'`; `build.py` rc 0; `retirement check` sin fila `pron`; después commit/push y `deskops message send`. Nada ejecutado.

FUTURO
IR recibe el hash y actualiza su acta/gate; IR o un humano decide el cierre de IR13 y el retiro de spec2viz; deskops transporta el mensaje. No hay hijos que transferir.
