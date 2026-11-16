# result-summary — ejecutor deskops-e-fe40ac7a9ef8-a2 (pron, IR13), ciclo de corrección 2

Evidencia completa (comandos, salidas y rc, en orden): `validation.log`. Diff de los cuatro archivos: `git-diff.txt`. Estado: `git-status.txt`.

## Verificación de p1-p4 (ya estaban; no se reaplicó nada)

- **p1**: `specir` en `/home/robocop/.local/bin/specir` (uv tool `specir v0.1.0`). El `uv-receipt.toml` registra `specir` editable desde `/mnt/ssd/proyectos/SLDB_1/IR` y `structuredlanguagedb` editable desde `/home/robocop/herramientas/sldb`. Dentro del venv, `sldb` se importa desde `/mnt/ssd/herramientas/sldb/src/sldb/__init__.py`, porque `/home/robocop/herramientas` es un symlink a `/mnt/ssd/herramientas`: son el mismo checkout. `specir diagram validate --help`, `specir diagram render --help` (acepta `--backend`/`--renderer` y `--out`) y `specir catalog build --help` (acepta `--config` y `--out`) salen con rc 0.
- **p2**: en `build.py`, las líneas 22-24 llaman a `run('specir', ...)` con los mismos argumentos que antes. Los docstrings de las líneas 1 y 30 coinciden con el texto exacto del TaskDoc.
- **p3**: en el README, la línea 14 dice `` `specir` `` y la línea 20 dice «Comandos principales del CLI de specIR». Los tres comandos de las líneas 23-25 usan `specir`. La línea 5 sigue sin tocar, como pide el TaskDoc.
- **p4**: la viñeta del CHANGELOG está una sola vez (`grep -c` = 1), al final de `## Sin publicar`. No se duplicó.

## Cambios de este ciclo (p3b)

Antes de editar, cada texto citado aparecía exactamente una vez (conteo 1). El reemplazo verifica `count == 1` y no hubo conflicto.

- (i) En `docs/spec2viz/specs/target.components.yml`:
  - línea 121: `label: verbo de acción, o verbo transitivo afirmado}` pasa a `label: "verbo de acción, o verbo transitivo afirmado"}`;
  - línea 128: `label: nodos, tags, contención}` pasa a `label: "nodos, tags, contención"}`.

  Nada más del spec cambió: el diff tiene solo esas 2 líneas.
- (ii) En `docs/spec2viz/build.py:46`, en la llamada a `mmdc` de `export_views`, `'-w', '1800'` pasa a `'--size', '1800'`.

## Validation (en orden)

| | Comando | Resultado |
|---|---|---|
| V1 | `grep -nE "run\('spec2viz'" docs/spec2viz/build.py` | sin salida (rc 1 de grep) ✅ |
| V2 | `cd docs/spec2viz && PATH=/mnt/ssd/herramientas/mermaid-cli:$PATH TMPDIR=/dev/shm python3 build.py` | rc 0, imprime `Generated 4 SVGs, diagrams.md and offline.html` ✅ (4 specs OK, 4 .mmd, index.html) |
| V3 | `IR/.venv/bin/specir retirement check ... \| grep -P '^\s*pron\t'` | sin filas de pron (PIPESTATUS `1 1`: rc 1 global esperado por otros repos, y el grep sin coincidencias) ✅ |

## Desvíos o dudas

- No hubo desvíos. Solo se tocaron los cuatro archivos de `files`. Ninguno se agregó al índice: no hubo add, commit ni push.
- V2 regeneró salidas ignoradas por git (`out/`, `index.html`, `offline.html`, `diagrams.md`). No aparecen en `git status`.
- `git status` también muestra cambios en `desk/`, `.deskops.log` y en otros run dirs. Ya estaban antes de este ciclo y no son míos.
- Para el commit de p5: el TaskDoc enumera build.py, README.md y CHANGELOG.md, pero ahora `docs/spec2viz/specs/target.components.yml` también está modificado por p3b y forma parte de `files`. Hay que incluirlo en el commit.
