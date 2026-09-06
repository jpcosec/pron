# 3. Unidad fundamental: `ExecutableNode`

Todo elemento ejecutable implementa el mismo contrato abstracto.

```clojure
(defprotocol ExecutableNode

  ;; identidad semántica
  (self-doc [node])

  ;; contrato
  (input-ports [node])
  (output-ports [node])

  ;; conocimiento al que tiene acceso
  (knowledge-projection [node])

  ;; capacidades declaradas
  (capabilities [node])

  ;; comportamiento temporal
  (state-machine [node])

  ;; backend que materializa la ejecución
  (runtime [node])

  ;; condiciones que prueban que terminó correctamente
  (completion-tests [node])

  ;; ejecución
  (execute [node context input]))
```

Conceptualmente:

```text
ExecutableNode
├── Self
├── Inputs
├── Outputs
├── Knowledge
├── Capabilities
├── State Machine
├── Runtime
├── Completion Tests
└── Implementation
```

La clase base debe mantenerse deliberadamente pequeña.

---

