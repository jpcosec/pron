#!/bin/sh
# Install the mounted worktrees editable (no network: dependencies are in the image), then run.
set -e
for pkg in $EDITABLE; do
    pip install -q --no-deps --no-build-isolation -e "$pkg"
done
exec "$@"
