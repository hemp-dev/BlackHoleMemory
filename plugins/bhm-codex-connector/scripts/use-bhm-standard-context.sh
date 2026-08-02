#!/usr/bin/env bash
# POSIX script to switch to standard profile
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

if command -v uv >/dev/null 2>&1; then
    exec uv run --directory "$PROJECT_ROOT" python -m blackholememory.cli profile set standard
else
    exec python3 -m blackholememory.cli profile set standard
fi
