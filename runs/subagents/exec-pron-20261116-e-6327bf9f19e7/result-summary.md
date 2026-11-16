# Resultado del ejecutor deskops-e-6327bf9f19e7 (pron, IR13), intento 1

**Estado: BLOQUEADO en p1.** No se tocó ningún archivo de pron (`git-diff.txt` vacío). p2–p4 y la validación de p5 no se ejecutaron.

## p1: instalar specir como herramienta uv

- `uv tool list | grep -A2 specir`: sin salida, así que se usó la rama sin `--reinstall`.
- `uv tool install --editable /mnt/ssd/proyectos/SLDB_1/IR`: rc 0. Instaló los ejecutables `specir` y `specir-install` en `~/.local/bin`.
- `specir diagram validate --help`, `specir diagram render --help` y `specir catalog build --help`: los tres dan **rc 1** con el mismo error:
  `ImportError: cannot import name 'SpecView' from 'sldb.api.matching'`
  (`~/.local/share/uv/tools/specir/lib/python3.13/site-packages/sldb/api/matching/__init__.py`).

Salida completa en `validation.log`.

## Causa (diagnosticada sin modificar nada)

- `IR/pyproject.toml` declara `structuredLanguageDB` sin `[tool.uv.sources]`. Por eso `uv tool install` lo resolvió
  desde PyPI: `structuredlanguagedb==0.1.13`, publicada y sin `SpecView`.
- `IR/.venv` (el que usa la comprobación de retiro) tiene sldb **editable** desde `file:///mnt/ssd/proyectos/SLDB_1/sldb`,
  donde `sldb/api/matching/__init__.py:20` sí exporta `SpecView`. Por eso `IR/.venv/bin/specir` funciona y la herramienta uv no.

## Lo que queda instalado

La herramienta uv `specir` quedó instalada pero rota en `~/.local/bin/specir`. No la desinstalé: la rama `--reinstall`
de p1 la reemplaza al reintentar.

## Opciones para el coordinador (no aplicadas: se apartan del texto de p1)

1. Reinstalar con el sldb local:
   `uv tool install --reinstall --editable /mnt/ssd/proyectos/SLDB_1/IR --with-editable <checkout de sldb>`.
   El checkout puede ser `/mnt/ssd/proyectos/SLDB_1/sldb`, que es el que usa `IR/.venv`, o la instalación única
   `/home/robocop/herramientas/sldb`. Luego se repiten los tres `--help`. Hay que corregir el p1 del TaskDoc.
2. Que sldb publique una versión con `SpecView` en PyPI y reintentar p1 tal cual.
3. Que IR agregue `[tool.uv.sources]` para sldb. Es un cambio en el repo IR, fuera del alcance de esta tarea.

## Desvíos

Ninguno. Me detuve según la regla del brief: «Si p1 falla, para sin tocar pron y repórtalo».
