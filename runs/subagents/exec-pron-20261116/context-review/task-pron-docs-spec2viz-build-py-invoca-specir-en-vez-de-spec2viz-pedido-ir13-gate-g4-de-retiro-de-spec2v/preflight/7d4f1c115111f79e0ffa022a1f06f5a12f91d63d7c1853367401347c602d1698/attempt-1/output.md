REFORMULACION
Propósito: eliminar la última dependencia de pron con spec2viz (pedido IR13, gate G4). Resultado: docs/spec2viz/build.py invoca `specir diagram validate`, `specir diagram render` y `specir catalog build` con los mismos argumentos; `python3 docs/spec2viz/build.py` termina rc 0 sin spec2viz en el camino; commit en master pusheado y mensaje a IR con su hash. Repo: pron (cwd). Límites: no renombrar docs/spec2viz ni tocar sus specs/catalog.yml; no regenerar ni commitear out/, index.html, offline.html, diagrams.md; no tocar IR, spec2viz ni sldb; no desinstalar spec2viz; la política de .gitignore de .sldb/ queda fuera.

AMBIGUEDADES
1. "al final de la lista bajo '## Sin publicar'" (p4): no se dice qué hacer si esa sección no existe; obligaría a inventar encabezado o ubicación alternativa.
2. "sin salida (el rc global sigue en 1 por otros repos)" (Validation, tercera comprobación): el comando acaba en `| grep -P '^\s*pron\t'`, cuyo rc es el de grep, no el de specir; no queda claro si basta la ausencia de salida o qué rc cuenta como verde. Obligaría a inventar el criterio.
3. "<hash del commit de p5>" (p6): no se especifica hash completo o corto ni formato del cuerpo; obligaría a elegir uno.

DRY-RUN (hipotético, sin ejecutar)
Lecturas: build.py (líneas 1, 22-24, 30), README.md (14, 20-25), CHANGELOG.md y referencias citadas. Cambios previstos: p1 instalar specir con el comando uv indicado y comprobar los tres `--help`; p2 sustituir el primer argumento de los tres run() y los dos docstrings; p3 README; p4 CHANGELOG; p5 ejecutar las tres validaciones y commit/push; p6 enviar mensaje deskops. Dependencias: uv, checkout /home/robocop/herramientas/sldb y .venv de IR. Validaciones futuras: grep vacío, build rc 0 y retirement check sin fila de pron, antes de commitear.

FUTURO
IR recibe el hash y actualiza la fila de pron en acta-de-retiro.md (línea 53); un humano decide el cierre y la política de .gitignore de .sldb/.
