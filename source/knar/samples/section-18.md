# 18. Orquestador

El orquestador debería ser pequeño.

Responsabilidades:

```text
1. recibir objetivo
2. resolver capacidades necesarias
3. encontrar nodos compatibles
4. verificar tipos
5. construir execution graph
6. ejecutar
7. observar estados
8. verificar completion tests
9. persistir resultados
```

No debería contener conocimiento específico de aplicaciones.

Pseudocódigo:

```clojure
(defn satisfy [goal context]

  (let [capability (resolve-capability goal)
        node       (find-node capability)
        input      (resolve-inputs node context)]

    (assert-compatible input node)

    (let [result (execute node context input)]

      (run-completion-tests node result)

      result)))
```

---

