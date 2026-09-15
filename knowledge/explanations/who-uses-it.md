# Quién lo usa

## Question

¿Quién usa pron?

## Answer

legos declara `pron` como dependencia y habla con esta versión: su `PronWorld` (`legos/src/legos/bridges/pron_world.py`) abre un `World` y lee con forms (spec 13) a través de sesiones de solo lectura y `World.payload`. Un permiso de legos es el nombre de una proyección.

## Sources

- SpecDoc:spec-13
