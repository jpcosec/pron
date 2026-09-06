# Plan de Refactorización de la CLI de Knowledge

Este documento describe la estrategia para reemplazar el script monolítico actual (`knowledge`) por una arquitectura modular, extensible y de menor huella de código, utilizando como punto de partida la base desarrollada en la instancia de prueba (`gemini_test/knowledge_base`).

## 1. Objetivo
Transformar la herramienta `knowledge` (actualmente un script Python de ~20KB que procesa archivos mediante expresiones regulares) en un paquete nativo de Python que delegue la carga pesada (parseo, indexación y relaciones) directamente a los motores **SLDB** y **KGDB**, volviéndolo lo más pequeño y extensible posible.

## 2. Migración Estructural (El Paquete)
En lugar de tener un único archivo ejecutable en la raíz, copiaremos la estructura base de `knowledge_base` y la renombraremos a `knowledge/`.

**Estado actual:**
```text
/home/jp/proyectos/knowledge/
└── knowledge (Script monolítico ejecutable)
```

**Estado propuesto:**
```text
/home/jp/proyectos/knowledge/
└── knowledge/
    ├── __init__.py
    ├── __main__.py      # Permite la ejecución con `python -m knowledge`
    ├── cli.py           # Enrutador de comandos y handlers
    ├── parser.py        # Definición limpia de argumentos y flags de argparse
    └── operations.py    # Capa lógica que dialoga con SLDB y KGDB
```

## 3. Limpieza de Dependencias (Desacoplamiento)
El código de `operations.py` traído de la base contiene acoplamiento a los modelos específicos de un agente en particular (`from kb_agent.models.knowledge import RuleAtom, TraitAtom...`).

**Acción:** 
- Eliminar toda referencia estática a `kb_agent`.
- Hacer que la herramienta sea genérica consultando directamente los modelos estructurales de este repositorio a través de SLDB (ej. `StructuredNLDoc`, `KnowledgeAtomDoc`).
- La tipología de átomos será validada por los contratos nativos de SLDB, no por clases hardcodeadas en Python.

## 4. Reemplazo del Motor Lógico
El script actual realiza un esfuerzo manual intenso (ej. `FRONTMATTER_RE`, parsing de YAML a mano, validación de tags) para leer los archivos `.md`.

**Acción:**
- Descartar el parseo manual por regex.
- En `operations.py`, utilizar los conectores nativos para cargar los documentos: `sldb.store.query.load_runtime_documents`.
- Utilizar `KGDBReader` para resolver la taxonomía, las dependencias semánticas y la exploración de nodos (ej. recuperar hermanos o padres en el grafo).

## 5. Fusión y Actualización de Comandos
El CLI propuesto mantendrá los comandos esenciales que ya existen, pero los ruteará a través del nuevo paquete:

- **`list` / `show`:** Se portarán los comandos actuales desde el script viejo hacia `cli.py`, pero invocarán a `KnowledgeOperations` para obtener los datos desde SLDB, eliminando la necesidad de leer el disco directamente.
- **`explore` / `navigate`:** Se heredan gratuitamente las capacidades de navegación en grafos implementadas en la base nueva, permitiendo consultar transiciones, metadatos y contextos en KGDB.

---
**Conclusión:** Al implementar este diseño, el código que debe mantenerse dentro de este repositorio se reduce al mínimo absoluto (solo lógica de interfaz), mientras que las reglas de negocio, validación de schemas y relaciones topológicas son delegadas exitosamente a SLDB y KGDB.
