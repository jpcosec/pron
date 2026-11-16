## REFORMULACION
Propósito: cumplir IR13/G4 retirando la única dependencia de spec2viz en pron. Resultado: `docs/spec2viz/build.py` invoca `specir` en validate/render/catalog build con los mismos argumentos; README y CHANGELOG actualizados; `build.py` rc 0 sin spec2viz; commit en master pusheado y hash enviado a IR. Repo: pron. Límites: solo tres `run()` (líneas 22-24), docstrings indicados, README líneas 14 y 20-25, viñeta CHANGELOG, instalar specir vía uv y mensaje a IR; no renombrar `docs/spec2viz`, no commitear `out/`, no tocar IR/spec2viz/sldb, no desinstalar spec2viz ni política `.gitignore`. Nodo ejecutable `task.code`, no agregado.

## AMBIGUEDADES
1. “commit ... en master y push a origin” no fija mensaje de commit; obliga a inventar asunto/cuerpo.
2. “al final de la lista bajo '## Sin publicar'” presupone que existen sección y lista; si faltan, obliga a inventar su creación/ubicación.
3. “si alguno falla, parar y reportar sin tocar pron” no indica canal ni destinatario del reporte; obliga a inventar el medio.
4. “mismo formato de viñeta” no muestra el formato vigente; si el CHANGELOG no lo hace evidente, obliga a inventar guion/negrita/espaciado.

## DRY-RUN
Lecturas: `build.py`, `README.md`, `CHANGELOG.md`, `uv tool list`, ayudas de specir, correspondencia/acta IR si hace falta. Cambios: p1 instalar/reinstalar specir editable y comprobar tres `--help`; p2 sustituir primer argumento en tres `run()` y dos docstrings exactos; p3 README frase y bloque de comandos; p4 viñeta CHANGELOG; p5 validaciones en orden sobre árbol de trabajo, commit y push; p6 mensaje a IR con hash. Dependencias: uv, `/mnt/.../IR`, red para push, deskops. Validaciones futuras: grep sin salida; `build.py` rc 0 y salidas; retirement check sin fila pron. Sin ejecutar.

## FUTURO
IR consume el mensaje/hash y actualiza `acta-de-retiro`/gate G4; un humano o nodo de IR decide el cierre de G4. Las salidas regeneradas quedan fuera del commit. Pron no desinstala spec2viz.
