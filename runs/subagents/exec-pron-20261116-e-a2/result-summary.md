# Resultado del ejecutor deskops-e-86f5d629bc99-a2 (intento 2): BLOQUEADO en la validación V2

## Pasos

- **p1, OK.** Corrí `uv tool install --reinstall --editable /mnt/ssd/proyectos/SLDB_1/IR --with-editable /home/robocop/herramientas/sldb` y salió con rc 0. structuredlanguagedb ahora viene de `file:///home/robocop/herramientas/sldb` y no de PyPI. `specir diagram validate --help`, `specir diagram render --help` (acepta `--backend` y `--out`) y `specir catalog build --help` (acepta `--config` y `--out`) salen con rc 0. `specir` está en `/home/robocop/.local/bin/specir`. La evidencia está en `p1.log` y al principio de `validation.log`.
- **p2, OK.** En `docs/spec2viz/build.py` cambié el primer argumento de las tres llamadas `run()` de `spec2viz` a `specir`. También cambié los dos docstrings, con el texto exacto que pide el TaskDoc. No toqué nada más.
- **p3, OK.** En `docs/spec2viz/README.md`, la frase de requisitos ahora dice «con `specir`, `mmdc`, Python y PyYAML disponibles». El encabezado quedó en «CLI de specIR» y los tres comandos usan `specir`.
- **p4, OK.** Agregué la viñeta al final de la lista bajo `## Sin publicar` de `CHANGELOG.md`, con el texto exacto.

## Validación (p5, sobre el árbol de trabajo)

- **V1, OK.** `grep -nE "run\('spec2viz'" docs/spec2viz/build.py` no da salida (rc 1).
- **V2, FALLA.** `cd docs/spec2viz && python3 build.py` termina con rc 1. `specir diagram validate` rechaza `specs/target.components.yml`:
  `unknown key 'data.edges.16.o verbo transitivo afirmado'; unknown key 'data.edges.23.tags'; unknown key 'data.edges.23.contención'`.
- **V3, OK.** `specir retirement check ... | grep -P '^\s*pron\t'` no da salida. El rc del pipeline es 1, que es lo esperado.

## Por qué V2 falla y por qué paré

- **No lo causa la migración.** El error viene de antes. `spec2viz diagram validate specs/*.yml` da exactamente el mismo error, con rc 1, y `specs/` no tiene cambios (está registrado en `validation.log`). Con spec2viz, `build.py` también fallaba en master.
- **La causa es YAML sin comillas** en `specs/target.components.yml` (último commit e7e92f0):
  - Línea 121: `label: verbo de acción, o verbo transitivo afirmado}`. En flow mapping, la coma corta el valor, y «o verbo transitivo afirmado» queda como una clave aparte.
  - Línea 128: `label: nodos, tags, contención}`. Por lo mismo, `tags` y `contención` quedan como claves sueltas.
- **El arreglo** es entrecomillar esos dos labels, por ejemplo `label: "verbo de acción, o verbo transitivo afirmado"` y `label: "nodos, tags, contención"`.
- **Por qué no lo apliqué:** ese archivo está fuera de los tres que el brief me permite tocar, y el TaskDoc deja fuera de alcance los specs. Por la regla del brief («si no se arregla así, para y repórtalo»), paré.

## Para el coordinador

- **Ampliar el alcance:** hay que sumar `docs/spec2viz/specs/target.components.yml` a `files` y a Scope (es un cambio de dos líneas). Otra opción es abrir una tarea aparte. Después hay que volver a correr V2.
- **Salidas generadas:** `out/mermaid/*.mmd` e `index.html` son de corridas anteriores (`index.html` es del 17 de septiembre). Esta corrida no las regeneró, porque se detuvo en el validate.
- **Mención de spec2viz que queda:** el README todavía dice «Catálogo navegable de spec2viz … CDN configurado por spec2viz» en la línea 5. Está fuera de las líneas que pide p3 (14 y 20-25), así que no lo cambié.
- **Restricciones:** no hice commit, push, `git add` ni `stash`, y no toqué `desk/` ni `.sldb/`. `git-status.txt` muestra que en pron solo cambiaron los tres archivos permitidos, más el desk y los runs que ya estaban así antes.
