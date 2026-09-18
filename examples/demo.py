"""Search the restaurant world and print what the plan would write.

python examples/demo.py --speak "(goal (book ana 6 terrace r-new ?t))"
python examples/demo.py --speak "(goal (free ?t))" --solutions
python examples/demo.py --show                         # the theorems of the world
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from worlds import restaurant  # noqa: E402

from plnr import Sym, ground, read_one, run, solutions, variables, write  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--speak", default="(goal (book ana 6 terrace r-new ?t))")
    ap.add_argument("--solutions", action="store_true", help="every answer, not the first")
    ap.add_argument("--budget", type=int, default=10_000)
    ap.add_argument("--show", action="store_true", help="the theorems, then the documents")
    args = ap.parse_args()

    world, theorems = restaurant.world(), restaurant.theorems()

    if args.show:
        for t in theorems.items:
            print(f"{t.name:<20} {t.kind:<11} {write(t.pattern)}")
        print()
        for doc in world.docs():
            print(f"{doc:<12} {world.model_of(doc):<12} {write(dict(world.payload(doc)))}")
        return 0

    goal = read_one(args.speak)
    if args.solutions:
        # only the variables of the goal as asked: the engine renames a theorem's own
        for b in solutions(goal, world, theorems, budget=args.budget):
            line = " ".join(f"{v} = {write(ground(Sym(v), b))}" for v in variables(goal))
            print(line or "(holds)")
        return 0

    plan = run(goal, world, theorems, budget=args.budget)
    for line in plan.trace:
        print(line)
    print()
    if not plan:
        print(f"no: {plan.reason}")
        return 1
    for name, value in plan.answers().items():
        print(f"  {name} = {write(value)}")
    print()
    for form in plan.as_forms():
        print(f"  {form}")
    print(f"\n{plan.spent} goals; nothing written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
