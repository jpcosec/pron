from __future__ import annotations

import sys
from pathlib import Path

from knowledge.operations import KnowledgeOperations
from knowledge.parser import build_parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    ops = KnowledgeOperations(
        store_path=Path(args.kb).resolve() if args.kb else Path.cwd()
    )

    if args.command == "list":
        return ops.list_atoms(args)
    elif args.command == "show":
        return ops.show_atom(args)
    elif args.command == "explore":
        return ops.explore(args)
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())