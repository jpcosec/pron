# Dependencias

## Question

¿De qué depende pron?

## Answer

- [sldb](https://github.com/jpcosec/hum-ecosystem) — ver `constraints.txt` para el commit exacto. Ya no depende de kgdb: sus tipos de relación y su grafo de aristas se fusionaron dentro de sldb.
- plnr, el motor de metas que evalúa `(goal …)`: viene dentro de pron (`src/plnr/`, misma distribución), no se instala aparte. Ver [`docs/PLNR.md`](docs/PLNR.md).

## Sources
