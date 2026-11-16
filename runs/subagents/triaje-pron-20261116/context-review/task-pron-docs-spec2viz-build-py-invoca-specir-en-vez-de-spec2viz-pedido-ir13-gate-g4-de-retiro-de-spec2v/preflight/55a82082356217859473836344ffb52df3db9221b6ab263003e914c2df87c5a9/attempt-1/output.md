REFORMULACION
Nodo ejecutable, no agregado. Encargo: en el repo pron, eliminar la dependencia de spec2viz en `docs/spec2viz/build.py` haciendo que sus tres llamadas `run()` usen `specir` con los mismos argumentos; actualizar docstrings y `docs/spec2viz/README.md`; registrar el cambio en `CHANGELOG.md`; instalar `specir` como herramienta uv; validar que `python3 docs/spec2viz/build.py` termina con rc 0; commitear y pushear en master; enviar a IR por `deskops message send` el hash del commit. Límites: no renombrar el directorio ni specs/catalog.yml; no commitear salidas ignoradas; no tocar IR, spec2viz ni sldb; no desinstalar spec2viz; no decidir la política de `.gitignore` de `.sldb/`.

AMBIGUEDADES
1. “agregar la entrada a CHANGELOG.md”: no fija formato, sección ni texto. Obliga a inventar redacción y ubicación.
2. “actualizar los docstrings de las líneas 1 y 30 para que digan specIR”: no da frase exacta ni si debe cambiar solo el nombre del comando. Obliga a inventar la redacción.
3. “instalar specir en la máquina como herramienta de uv” y “uv tool install --editable …”: no indica qué hacer si ya está instalado o si hay versión previa. Obliga a inventar reinstalación/verificación.
4. Validación: `grep -n "'spec2viz'" docs/spec2viz/build.py # sin salida` frente a Done When: “grep de 'spec2viz' como comando … vacío”. No aclara si basta el patrón entrecomillado o una búsqueda semántica. Obliga a inventar el criterio.

DRY-RUN
Lecturas futuras: task doc, `docs/spec2viz/build.py`, README, CHANGELOG, correspondencia CLI y acta de retiro. Cambios previstos: instalar specir; sustituir `'spec2viz'` por `'specir'` en líneas 22-24; ajustar docstrings; actualizar README; añadir CHANGELOG. Dependencias: uv, repo IR con `specir`, `/dev/shm`, `deskops`. Validaciones futuras: grep sin coincidencias; ejecutar build.py con rc 0; `specir retirement check` sin fila pron; commit pusheado; mensaje con hash. No se ejecuta nada.

FUTURO
El ejecutor produce el commit y su hash; IR consume el mensaje y decide el estado en su acta. Un humano resuelve las ambigüedades anteriores antes de ejecutar.
