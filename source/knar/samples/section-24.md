## 24. La arquitectura reducida

Al final, el sistema tiene cinco conceptos fundamentales:

```text
KNOWLEDGE
    conocimiento semántico persistido

NODE
    componente que promete una transformación

PORT
    contrato tipado entre componentes

RUNTIME
    mecanismo que materializa la transformación

PROJECTION
    representación particular del conocimiento
```

Y alrededor de ellos:

```text
State Machines
Capabilities
Completion Tests
Permissions
Provenance
Orchestration
```

Eso permite que un scraper, un LLM, PostgreSQL, una API, un generador Astro o incluso otro sistema multiagente **sean piezas del mismo sistema sin fingir que internamente hacen lo mismo**.

