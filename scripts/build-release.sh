#!/usr/bin/env bash
# Build BlackHoleMemory release artifacts for macOS and Linux
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "==> Building BlackHoleMemory Release Bundle..."

BUILD_DIR="$PROJECT_ROOT/dist/release"
mkdir -p "$BUILD_DIR"

if command -v uv >/dev/null 2>&1; then
    uv sync --extra build
    PYTHON_BIN="uv run python"
else
    PYTHON_BIN="python3"
fi

echo "--> Generating PyInstaller release executable..."
$PYTHON_BIN -m PyInstaller --clean --noconfirm "$PROJECT_ROOT/BHM_Launcher.spec"

echo "[OK] Release build completed in $PROJECT_ROOT/dist"
