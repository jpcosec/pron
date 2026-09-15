# Verificar cambios

## Question

¿Cómo verifico cambios?

## Answer

Con SLDB y KGDB instalados en el entorno:

```bash
python -m pip install -e '.[dev]'
make check          # lint, formato, tipado, tests y documentación
make test           # suite local, sin plugins externos de pytest
make format         # aplica formato; check solo lo verifica
```

También existen `make lint`, `make format-check`, `make typecheck` y `make docs-check`.
Ruff, mypy y pytest tienen versiones fijadas en el extra `dev`. El chequeo de mypy
cubre las anotaciones existentes; todavía no exige tipado estricto en todo pron.
Para regenerar documentación tras un cambio de contrato, usa `pron docs --world . --pythonpath .`.

## Sources

- CliCommandDoc:cmd-pron-docs
