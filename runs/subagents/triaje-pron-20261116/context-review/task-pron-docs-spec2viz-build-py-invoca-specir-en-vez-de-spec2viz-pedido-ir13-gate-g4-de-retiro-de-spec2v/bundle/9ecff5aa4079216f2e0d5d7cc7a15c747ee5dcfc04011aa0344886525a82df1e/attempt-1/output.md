REFORMULACION

Propósito: que pron elimine su única dependencia de spec2viz y cumpla el pedido IR13 (gate G4 de retiro). Resultado: `docs/spec2viz/build.py` invoca `specir` para validar, renderizar y construir el catálogo; README y CHANGELOG lo reflejan; `python3 docs/spec2viz/build.py` termina rc 0; commit en `master` pusheado a `origin`; mensaje a IR con el hash. Repo: pron (`/mnt/ssd/proyectos/SLDB_1/pron`). Límites: tocar solo los tres `run()` y dos docstrings de `build.py`, las líneas indicadas de README y una viñeta de CHANGELOG; instalar specir; no renombrar `docs/spec2viz` ni sus specs/catalog.yml; no commitear salidas generadas; no tocar IR, spec2viz ni sldb; no desinstalar spec2viz; la política de `.gitignore` de `.sldb/` queda fuera.

AMBIGUEDADES

1. “instalar specir en la máquina como herramienta de uv” frente a “cd /mnt/ssd/proyectos/SLDB_1/IR && .venv/bin/specir retirement check”: no queda claro si specir debe estar solo como herramienta uv en PATH o también en el `.venv` de IR. Obligaría a inventar qué binario usa `build.py` y cuál exige la validación.
2. “Correr la validación y commitear”: la sección Validation lista tres comprobaciones, pero no dice si “la validación” incluye las tres antes del commit o solo `build.py`. Obligaría a inventar el orden exacto y si se commitea antes de la comprobación de retiro.
3. “docs/spec2viz/build.py … líneas 22, 23 y 24” y “README.md (líneas 14 y 20-25)”: las referencias dependen de la numeración actual de los archivos. Si no coinciden, obligaría a inventar el mapeo por contenido.

DRY-RUN

Lecturas: TaskDoc, rituales, `build.py`, `README.md`, `CHANGELOG.md`, referencias de correspondencia y acta. Cambios previstos: instalar/reinstalar specir con uv; sustituir `spec2viz` por `specir` en las tres llamadas y los docstrings; actualizar README y CHANGELOG; commit/push; `deskops message send` a IR. Dependencias: `uv`, specir, `mmdc`, PyYAML, Python 3, checkout de IR y deskops. Validaciones futuras: grep sin `run('spec2viz'`; `build.py` rc 0; `specir retirement check` sin fila de pron. Sin ejecutar nada.

FUTURO

IR recibe el mensaje, verifica el commit y actualiza su acta de retiro; otro nodo o un humano decide la política de `.gitignore` de `.sldb/` y la retirada efectiva de spec2viz.
