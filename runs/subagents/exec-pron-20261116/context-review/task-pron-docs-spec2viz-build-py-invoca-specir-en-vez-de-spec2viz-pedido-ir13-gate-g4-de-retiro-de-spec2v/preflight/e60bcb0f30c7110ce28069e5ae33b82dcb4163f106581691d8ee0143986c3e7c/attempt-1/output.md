## REFORMULACION

Propósito: ejecutar la migración pedida por IR13/G4 para que pron deje de depender de spec2viz. Resultado: `docs/spec2viz/build.py` invoca `specir` en sus tres `run()`, documentación y CHANGELOG actualizados, validaciones en verde, commit pusheado y mensaje a IR con el hash. Repo: pron, con referencias externas a `../IR`, `../spec2viz` y `../sldb`. Límites: solo los tres `run()` y docstrings citados de `build.py`, líneas indicadas de README, CHANGELOG, instalación de specir, commit/push y mensaje; no renombrar el directorio ni specs/catalog, no regenerar/commitear salidas, no tocar IR/spec2viz/sldb, no desinstalar spec2viz ni decidir la política de `.gitignore` de `.sldb/`.

## AMBIGUEDADES

1. “commit de build.py, README.md y CHANGELOG.md en master y push a origin”: no fija mensaje de commit ni qué hacer con cambios locales no relacionados. Obliga a inventar el mensaje y la política de staging.
2. “si 'uv tool list' ya muestra specir” / “si alguno falla, parar y reportar sin tocar pron”: no define qué hacer si `uv` no existe, falla o no puede listar. Obliga a inventar el fallback o el criterio de aborto.
3. “al final de la lista bajo '## Sin publicar'”: no indica qué hacer si esa sección no existe o está vacía. Obliga a inventar si se crea o dónde se inserta.
4. “specir retirement check ... | grep -P '^\s*pron\t'”: no aclara si el ejecutor debe interpretar el rc global 1 como aceptable únicamente si no hay filas de pron. Obliga a inventar el criterio exacto de éxito.

## DRY-RUN

Lecturas: `docs/spec2viz/build.py`, `README.md`, `CHANGELOG.md`, la nota del inbox, `../IR/docs/spec2viz/correspondencia-cli.md` y `acta-de-retiro.md`. Comprobaría `uv tool list` y los `--help` de los tres comandos specir. Cambios previstos: p1 instalar/reinstalar specir editable; p2 sustituir solo el primer argumento de las tres llamadas y los dos docstrings; p3 actualizar README; p4 añadir viñeta al CHANGELOG; p5 ejecutar las tres validaciones y, en verde, commit/push; p6 enviar el mensaje a IR. Dependencias: `uv`, specir, Python 3, PyYAML y mmdc. Validaciones futuras: grep sin resultados, `python3 build.py` rc 0 y `specir retirement check` sin fila de pron.

## FUTURO

Un nodo ejecutor aplicará p1-p6. IR recibirá el hash y verificará el retiro; un humano decidirá el mensaje de commit y cómo actuar ante fallos no cubiertos.
