#!/usr/bin/env bash
# POSIX script to run BlackHoleMemory service on macOS and Linux
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

export PYTHONPATH="$PROJECT_ROOT/src:${PYTHONPATH:-}"
export BHM_HOST="${BHM_HOST:-127.0.0.1}"
export BHM_PORT="${BHM_PORT:-8000}"

if [ "${1:-}" = "--authoritative" ]; then
    export BHM_MEMORY_STORE_MODE="sqlite-authoritative"
    export BHM_FALLBACK_MODE="explicit"
    export BHM_PROJECTION_WORKER_ENABLED="false"
fi

if command -v uv >/dev/null 2>&1; then
    exec uv run uvicorn blackholememory.app:app --host "$BHM_HOST" --port "$BHM_PORT"
else
    exec python3 -m uvicorn blackholememory.app:app --host "$BHM_HOST" --port "$BHM_PORT"
fi
