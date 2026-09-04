from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="knowledge",
        description="knowledge: CLI modular para gestionar átomos y la base de conocimiento.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--kb", default=".", help="Ruta al root de la KB (default: .)")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    p = subparsers.add_parser("list", help="Lista todos los átomos en la base de conocimiento")
    p.add_argument("--format", choices=["text", "json"], default="text", help="Formato de salida")

    # show
    p = subparsers.add_parser("show", help="Muestra un atom completo")
    p.add_argument("selector", help="Id del atom o fragmento del nombre")
    p.add_argument("--format", choices=["text", "json"], default="text", help="Formato de salida")

    # explore (stub for future KGDB/SLDB expansion)
    p = subparsers.add_parser("explore", help="Navegación del grafo o tags (Extensible vía SLDB/KGDB)")
    p.add_argument("query", nargs="?", default=None, help="Consulta de exploración")

    return parser