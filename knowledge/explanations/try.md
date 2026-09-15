# Probar

## Question

¿Cómo lo pruebo?

## Answer

```bash
pip install -e .            # sldb y kgdb del ecosistema, instalados editables
python -m pytest -q tests   # cada test monta un mundo real desde cero
```

## Sources
