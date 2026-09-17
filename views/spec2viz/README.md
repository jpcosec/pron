# pron — Diagramas de arquitectura

Vistas de `pron`: la arquitectura objetivo, proyección gráfica de [`source/spec`](../../source/spec/README.md) (`target.*.yml`), y las capas reales de código (`codigo.capas.yml`, mapeo de la tabla "Capas" de [`../../README.md`](../../README.md)). Cuando el spec o el código cambien, se edita el `specs/*.yml` correspondiente y se regenera todo con `build.py`; no se editan los archivos de `out/` ni los HTML directamente. La vista de la arquitectura v1 está en la rama `v1-code-and-kb`.

- [Catálogo navegable de spec2viz](index.html): filtros, navegación y herramientas del visor nativo. Carga Mermaid desde el CDN configurado por spec2viz.
- [Visor sin conexión](offline.html): el SVG está integrado en un único HTML, sin dependencias de red.
- [Diagrama en Markdown](diagrams.md): Mermaid y notas de lectura.
- [SVG](out/svg/): archivo para abrir o compartir.

## Fuentes y regeneración

`specs/*.yml` son las fuentes semánticas de los diagramas. `catalog.yml` contiene sus descripciones y notas de interpretación. Los archivos de `out/`, los HTML y `diagrams.md` son generados.

Desde este directorio, con `spec2viz`, `mmdc`, Python y PyYAML disponibles:

```bash
python build.py
```

Comandos principales del CLI de spec2viz:

```bash
spec2viz diagram validate specs/*.yml
spec2viz diagram render specs/*.yml --backend mermaid --out out/mermaid
spec2viz catalog build --config catalog.yml --out index.html
```

`python build.py --exports-only` regenera SVG, Markdown y visor sin conexión a partir del Mermaid ya producido.

## Agregar una vista nueva

1. Escribir `specs/<nombre>.yml` (tipo `component`, `class`, `sequence`, `state`, `activity`, `deployment` o `component_view_matrix` según corresponda).
2. Agregar un `item` en `catalog.yml` con su `id`, `desc`, `nav`, `specs` y `notes`.
3. Correr `python build.py`.
