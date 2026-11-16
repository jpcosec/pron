# Brief del tester deskops-t-69a6715f4520 (pron, IR13)

Eres el **tester independiente** de una tarea del desk de pron, con el rol `deskops-tester` en modo tester. No
implementas, no corriges, no ruteas y no cierras: compruebas y entregas evidencia. No ves la conversación del
coordinador ni el informe del ejecutor, y **no debes leer** otros run dirs.

- Repo: `/mnt/ssd/proyectos/SLDB_1/pron`, rama `master`. Haz `cd` ahí. Tu pane arrancó en `/mnt/ssd/proyectos/SLDB_1`
  solo por el diálogo de confianza.
- TaskDoc (el contrato):
  `desk/tasks/task-pron-docs-spec2viz-build-py-invoca-specir-en-vez-de-spec2viz-pedido-ir13-gate-g4-de-retiro-de-spec2v.md`
- Run dir (tu evidencia): `runs/subagents/exec-pron-20261116-t-c2/`. Su `run.md` es del coordinador: no lo edites.
- Los cambios del ejecutor están en el árbol de trabajo, sin commitear, en los cuatro archivos de `files` del TaskDoc.

## Qué compruebas

1. **El diff contra el contrato.** Corre
   `git diff -- docs/spec2viz/build.py docs/spec2viz/README.md docs/spec2viz/specs/target.components.yml CHANGELOG.md`
   y contrasta cada hunk con Scope e Implementation Path del TaskDoc:
   - ¿cambió solo lo permitido?
   - ¿los textos exactos (docstrings, viñeta del CHANGELOG, labels entrecomillados, `--size`) coinciden?
   - ¿hay algo fuera de alcance?
2. **Ningún otro archivo de código cambió.** En `git status --short`, fuera de `desk/`, `runs/` y `.deskops.log`,
   solo deben aparecer esos cuatro archivos.
3. **Las tres comprobaciones de Validation del TaskDoc, en orden y tal cual.** La segunda lleva
   `PATH=/mnt/ssd/herramientas/mermaid-cli:$PATH`.
   - V1: sin salida.
   - V2: rc 0 e imprime `Generated 4 SVGs, diagrams.md and offline.html`.
   - V3: sin filas de pron. El rc 1 del pipeline es lo esperado.
4. **El uso real de specir.** Confirma que `specir` del PATH es el que corre `build.py` (`command -v specir`) y que
   `specir diagram validate docs/spec2viz/specs/*.yml` da rc 0.
5. **Que no hay salidas generadas en el índice.** `git status --short docs/spec2viz` no debe listar `out/`,
   `index.html`, `offline.html` ni `diagrams.md`.

## Reglas

- Usa `TMPDIR=/dev/shm`.
- No edites ningún archivo del repo. Correr `build.py` regenera salidas ignoradas, y eso está bien.
- Prohibido: `git add`, `git commit`, `git stash`, `git checkout`, `git restore`, `git push`, `pkill`, `pgrep`.
  Tampoco instales nada.

## Qué entregas, en el run dir

- `test.log`: cada comando con su salida completa y su rc.
- `result-summary.md`: un veredicto `PASS` o `FAIL` en la primera línea; después, cada comprobación (1 a 5) con
  su resultado y evidencia. Si es FAIL, cuenta qué falló exactamente.

Al terminar, responde en una línea: `TEST PASS: <ruta>` o `TEST FAIL: <ruta>`.
