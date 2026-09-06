# 8. Runtime

El runtime es el backend de ejecución.

```text
ExecutableNode
        │
        ▼
 Runtime Adapter
```

Posibles runtimes:

```text
LLMRuntime
SQLRuntime
HTTPRuntime
ShellRuntime
ClojureRuntime
JSRuntime
WASMRuntime
AstroRuntime
DeepSeekHarnessRuntime
HumanRuntime
```

Interfaz mínima:

```clojure
(defprotocol Runtime
  (prepare [runtime node context])
  (invoke [runtime request])
  (observe [runtime execution])
  (cancel [runtime execution]))
```

Esto permite cambiar DeepSeek Harness por otro sistema sin alterar el modelo semántico.

---

