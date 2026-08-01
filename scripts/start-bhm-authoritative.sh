#!/usr/bin/env bash
# Start BlackHoleMemory authoritative runtime on macOS and Linux
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "==> Initializing BlackHoleMemory Authoritative Runtime..."
export BHM_MEMORY_STORE_MODE="sqlite-authoritative"

if command -v uv >/dev/null 2>&1; then
    exec uv run python -m blackholememory.cli start "$@"
else
    exec python3 -m blackholememory.cli start "$@"
fi
