# Dependencias

## Question

¿De qué depende pron?

## Answer

- Python 3.12 o superior.
- [sldb](https://github.com/jpcosec/sldb) (la distribución `structuredLanguageDB>=0.1.12`); la CI lo instala desde `main`, sin releases todavía. Ya no depende de kgdb: sus tipos de relación y su grafo de aristas se fusionaron dentro de sldb.
- plnr, el motor de metas que evalúa `(goal …)`: viene dentro de pron (`src/plnr/`, misma distribución), no se instala aparte. Ver [`docs/PLNR.md`](docs/PLNR.md).

## Sources
