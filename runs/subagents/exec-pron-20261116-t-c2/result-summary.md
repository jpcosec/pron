PASS

# Tester deskops-t-69a6715f4520 — IR13 (pron docs/spec2viz/build.py → specir)

Repo `/mnt/ssd/proyectos/SLDB_1/pron`, rama `master`, HEAD `157171f`, cambios del ejecutor sin commitear en el árbol de trabajo.
Evidencia completa (comando, salida y rc) en `test.log`, en este mismo run dir. `TMPDIR=/dev/shm`.

## 1. Diff contra el contrato — PASS

`git diff` de los cuatro archivos de `files` (rc 0):

- `docs/spec2viz/build.py`
  - Docstring del módulo: `"""Rebuild the specIR catalog and portable SVG views from semantic YAML."""`. Coincide con el texto exacto.
  - Las tres llamadas `run('spec2viz', …)` de main() pasan a `run('specir', …)`. Solo cambia el primer argumento; el resto queda idéntico (validate, render con `--backend mermaid --out out/mermaid`, catalog build con `--config catalog.yml --out index.html`).
  - Docstring de export_views: `"""Export a specIR catalog with pre-rendered Mermaid to portable views."""`. Coincide con el texto exacto.
  - En mmdc, `'-w', '1800'` pasa a `'--size', '1800'`. No cambian otros argumentos.
- `docs/spec2viz/README.md`
  - En la línea de requisitos, `` `spec2viz` `` pasa a `` `specir` ``.
  - `Comandos principales del CLI de spec2viz:` pasa a `Comandos principales del CLI de specIR:`.
  - En los tres comandos, `spec2viz` pasa a `specir` y sus argumentos no cambian.
  - La mención de spec2viz de la línea 5 sigue intacta (está fuera del alcance) y no hay otros hunks.
- `docs/spec2viz/specs/target.components.yml`: solo se entrecomillaron los dos label (`"verbo de acción, o verbo transitivo afirmado"` y `"nodos, tags, contención"`). No cambió nada más.
- `CHANGELOG.md`: se añadió una viñeta al final de la lista bajo `## Sin publicar`, justo antes de `## 1.0.0`. Su texto coincide con el exacto del TaskDoc: `- docs/spec2viz/build.py valida, renderiza y arma el catálogo con specir en vez de spec2viz (pedido IR13 del gate de retiro de spec2viz).`

No hay nada fuera del alcance.

## 2. Ningún otro archivo de código cambió — PASS

Filtré `git -c core.quotePath=false status --short` excluyendo `desk/`, `runs/` y `.deskops.log`. Quedan:
- ` M` para CHANGELOG.md, docs/spec2viz/README.md, docs/spec2viz/build.py y docs/spec2viz/specs/target.components.yml.
- `?? .herdr-coordination.md`.

Nota: `.herdr-coordination.md` no es código ni lo produjo el ejecutor. Es el log de despacho de herdr (su cabecera es `dispatch -> w5:p17`, del 2026-11-16 02:31:01), no está ignorado y no hay que commitearlo. Lo señalo para que el coordinador no lo incluya en el commit.

## 3. Validation del TaskDoc, en orden — PASS

- V1: `grep -nE "run\('spec2viz'" docs/spec2viz/build.py` no da salida (rc 1 de grep, sin coincidencias).
- V2: `cd docs/spec2viz && PATH=/mnt/ssd/herramientas/mermaid-cli:$PATH TMPDIR=/dev/shm python3 build.py` sale con rc 0.
  - Los 4 specs dan `OK`.
  - Hay 4 `Rendered … .mmd` y `Rendered catalog -> index.html`.
  - La última línea es `Generated 4 SVGs, diagrams.md and offline.html`.
- V3: `.venv/bin/specir retirement check … | grep -P '^\s*pron\t'` no da salida (`PIPESTATUS=1 1`). El check completo sale con rc 1 por graph_ui, deskops, sldb, IR, spec2viz/.sldb y 13 filas no acreditadas, y no lista ninguna fila de pron. Ese rc 1 es lo esperado.

## 4. Uso real de specir — PASS

- `command -v specir` da `/home/robocop/.local/bin/specir`, un symlink a `~/.local/share/uv/tools/specir/bin/specir`, que es la herramienta uv.
- El uv-receipt dice `specir` editable de `/mnt/ssd/proyectos/SLDB_1/IR` y `structuredlanguagedb` editable de `/home/robocop/herramientas/sldb`, que resuelve a `/mnt/ssd/herramientas/sldb`. Las importaciones lo confirman: `specir` sale de `IR/src/specir`, `sldb` sale de `/mnt/ssd/herramientas/sldb/src/sldb`.
- build.py invoca `specir` sin ruta, así que en V2 corrió este binario.
- `specir diagram validate docs/spec2viz/specs/*.yml` sale con rc 0 y los 4 specs dan OK.

## 5. Sin salidas generadas en el índice — PASS

- `git status --short docs/spec2viz` solo lista README.md, build.py y specs/target.components.yml (los tres con ` M`).
- `out/`, `index.html`, `offline.html` y `diagrams.md` existen tras V2, pero `--ignored` los marca `!!` y `.gitignore` los cubre en las líneas 15 a 18.
- `git ls-files` no tiene ninguno de ellos versionado (grep rc 1).
