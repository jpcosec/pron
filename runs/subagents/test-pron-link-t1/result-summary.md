# Resultado del tester: test-pron-link-t1

**Veredicto: FALLA (incompleto).** Las comprobaciones 1–4 pasan. Las 5 y 6 no se pudieron correr: el sistema mató la suite por poca memoria. No hay indicios de un defecto en el cambio.

| # | Comprobación | Resultado | Evidencia |
|---|---|---|---|
| 1 | Diff según contrato | PASA | solo 4 archivos (+ `.deskops.log`/`runs/`); los `.sldb` cambian solo `path:` de deskops; el paso de `check.yml` va entre Install y check y coincide con p2; la viñeta coincide con p3 y queda antes de `## 1.0.0` (test.log) |
| 2 | V1, V2, V3, V7 | PASA | V1 rc 0 `- deskops -> ../deskops/.sldb`; V2 grep rc 1; V3 → `/mnt/ssd/proyectos/SLDB_1/deskops/.sldb`; V7 rc 0 (test.log) |
| 3 | V4+V5 con caché fría, V6 control | PASA | V4 rc 0, V5 rc 0, sin `No store_index` (v4-world.log, v5-docs.log); V6 rc 2 con `No store_index.yaml at /dev/herramientas/deskops/.sldb` (v6-control.log:60) |
| 4 | Layout del CI de pron | PASA | clone rc 0, `make world` rc 0, sin `No store_index` (gh-layout.log) |
| 5 | Suite completa | NO CORRIDA | proceso matado por presión de memoria (swap lleno) al ~60 %; suite.log truncado, 4 F sin nombre |
| 6 | test_01_world_store.py | NO CORRIDO | misma presión de memoria |

FAIL de la suite clasificados: no hay datos; la suite no terminó.

Pendiente: relanzar 5 y 6 cuando haya memoria libre (el comando del brief, con xdist ya instalado en el venv).
