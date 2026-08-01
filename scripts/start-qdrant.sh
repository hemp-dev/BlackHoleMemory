#!/usr/bin/env bash
# Start local Qdrant vector database container on macOS and Linux
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "==> Launching Qdrant container..."
if command -v uv >/dev/null 2>&1; then
    exec uv run python -m blackholememory.cli qdrant start "$@"
else
    exec python3 -m blackholememory.cli qdrant start "$@"
fi
