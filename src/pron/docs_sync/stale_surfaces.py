"""SurfaceDocs of modules that no longer exist (spec 08 step 9): untracked, and the file
generated for each under knowledge/surfaces deleted. With check, the drift is reported and
nothing is written.
"""

from __future__ import annotations

from typing import Any

from pron.world.world import World


class StaleSurfaces:
    """Removes, from one world, the SurfaceDocs no module generates anymore."""

    def __init__(self, world: World, check: bool) -> None:
        self.world = world
        self.check = check

    def __call__(self, specs: list[dict[str, Any]]) -> list[str]:
        store = self.world.store
        wanted = {spec["id"] for spec in specs}
        stale = sorted(
            d.name for d in store.docs_of("SurfaceDoc") if d.name not in wanted
        )
        generated = (self.world.root / "knowledge" / "surfaces").resolve()
        for name in [] if self.check else stale:
            path = store.doc_path("SurfaceDoc", name)
            store.untrack(name)
            if path is not None and path.resolve().parent == generated:
                path.unlink(missing_ok=True)
        return [f"SurfaceDoc {name} (stale)" for name in stale]
