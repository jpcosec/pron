## REFORMULACION
Encargo ejecutable de código en el repo **pron**: cumplir el pedido IR13 (gate G4) migrando la única dependencia de spec2viz de `docs/spec2viz/build.py` a specir. Resultado: las tres llamadas usan `specir diagram validate`, `specir diagram render` y `specir catalog build` con los mismos argumentos; `python3 docs/spec2viz/build.py` termina rc 0 sin spec2viz en ejecución; README, spec y CHANGELOG ajustados; commit en master pusheado; mensaje a IR con el hash. Límites: no renombrar `docs/spec2viz` ni sus specs/`catalog.yml`; no commitear salidas ignoradas; no instalar/cambiar mermaid-cli; no tocar IR, spec2viz ni sldb; no desinstalar spec2viz; no cambiar README línea 5 ni la política de `.gitignore` de `.sldb/`.

## AMBIGUEDADES
1. “con las tres en verde” choca con la tercera validación: “# sin salida (el rc global sigue en 1 por otros repos)”. Obliga a inventar si “verde” significa ausencia de fila `pron` o rc 0.
2. “commit de build.py, README.md y CHANGELOG.md en master y push a origin” no fija mensaje de commit; obliga a inventarlo.
3. “si cambiaron, ubicar cada cambio por el texto citado” no define qué hacer si el texto no aparece o aparece repetido; obliga a inventar criterio de búsqueda o aborto.

## DRY-RUN
Hipotético, sin ejecutar: leer task doc, nota de inbox, `correspondencia-cli.md`, `acta-de-retiro.md`, `build.py`, README, `target.components.yml` y CHANGELOG. Verificar uv/specir/mmdc y los `--help` de los tres comandos specir. Cambios previstos: instalar specir editable con sldb local; sustituir `'spec2viz'` por `'specir'` en líneas 22-24 y actualizar docstrings; README líneas 14 y 20-25; entrecomillar labels 121/128; `-w`→`--size`; añadir viñeta al CHANGELOG. Dependencias: instalación uv, wrapper mmdc en PATH y árbol listo para commit. Validaciones futuras: grep vacío; `build.py` rc 0 con la impresión esperada; retirement check sin fila `pron`. Después, commit/push y mensaje.

## FUTURO
IR, como otro nodo, consume el hash y actualiza su acta de retiro. Un humano decide ante fallos de instalación o validación que obliguen a parar sin tocar pron.
