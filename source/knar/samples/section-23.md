# 23. Invariantes

La primera versión debería imponer estas reglas:

1. Todo nodo tiene `SelfDoc`.
2. Todo input/output tiene tipo.
3. Todo nodo declara explícitamente qué conocimiento lee/escribe.
4. Ningún runtime define semántica del agente.
5. Todo nodo ejecutable posee al menos un completion test.
6. Un nodo no puede escribir fuera de su scope.
7. La compatibilidad de puertos se valida antes de ejecutar.
8. Todo resultado persistido debe poder rastrearse hacia la ejecución que lo produjo.
9. Workflows y aplicaciones pueden encapsularse nuevamente como nodos.
10. El grafo de conocimiento sigue siendo la fuente de verdad.

---

