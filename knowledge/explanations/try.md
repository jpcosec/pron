# Probar

## Question

¿Cómo lo pruebo?

## Answer

```bash
pip install -e .            # sldb del ecosistema, instalado editable
python -m pytest -q tests   # cada test monta un mundo real desde cero
```

## Sources
