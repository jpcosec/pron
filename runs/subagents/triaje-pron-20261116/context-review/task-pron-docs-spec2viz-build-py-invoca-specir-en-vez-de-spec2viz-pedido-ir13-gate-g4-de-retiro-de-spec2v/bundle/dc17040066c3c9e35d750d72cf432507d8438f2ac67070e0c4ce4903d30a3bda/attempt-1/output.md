## REFORMULACION

Nodo ejecutable (no agregado). Propósito: retirar la última dependencia de pron con spec2viz (IR13, gate G4) migrando sus invocaciones a specir. Repo: pron, rama master. Resultado: `docs/spec2viz/build.py` llama `specir diagram validate`, `specir diagram render` y `specir catalog build` con los mismos argumentos, docstrings y README/CHANGELOG actualizados, `python3 docs/spec2viz/build.py` con rc 0 sin spec2viz, retirement check sin filas de pron, commit pusheado y mensaje a IR con el hash. Límites: solo los tres `run()` y docstrings de build.py, README (líneas 14 y 20-25), CHANGELOG, instalación de specir como herramienta uv y el mensaje; fuera: renombrar `docs/spec2viz`, regenerar/commitear salidas, tocar IR/spec2viz/sldb, desinstalar spec2viz y la política de `.gitignore` de `.sldb/`.

## AMBIGUEDADES

1. «commit de build.py, README.md y CHANGELOG.md en master y push a origin»: no fija mensaje de commit; obliga a inventarlo.
2. «si 'uv tool list' ya muestra specir»: no define el criterio de coincidencia (paquete vs. entrada del binario).
3. «uv tool install --editable /mnt/ssd/proyectos/SLDB_1/IR»: no fija revisión del árbol IR ni si admite cambios sin commitear.
4. «sin salida (el rc global sigue en 1 por otros repos)»: no aclara si el rc 1 de la tubería cuenta como pase; "sin salida" y rc esperado se contradicen.
5. «al final de la lista bajo '## Sin publicar'»: posición exacta entre viñetas multilínea y formato de continuación no fijados.

## DRY-RUN

Lecturas: `docs/spec2viz/build.py`, `README.md`, `CHANGELOG.md`, las referencias de IR (correspondencia-cli, acta-de-retiro) y `uv tool list`. Cambios previstos: instalar specir editable; sustituir el primer argumento en las tres `run('spec2viz', ...)`; actualizar los dos docstrings a specIR; README (frase de requisitos, «CLI de specIR» y los tres comandos); viñeta en CHANGELOG. Dependencias: uv, mmdc, PyYAML y `specir` en PATH; el chequeo de retiro usa `/mnt/ssd/proyectos/SLDB_1/IR/.venv/bin/specir`. Validaciones futuras, en orden: grep vacío; build.py rc 0 sobre el árbol de trabajo; retirement check sin filas de pron; después commit/push y `deskops message send` con el hash.

## FUTURO

IR recibe el hash, actualiza la fila de pron en `acta-de-retiro.md` y decide el cierre de G4; una tarea aparte decide la política de `.gitignore` de `.sldb/`; la desinstalación de spec2viz queda fuera de este nodo.
