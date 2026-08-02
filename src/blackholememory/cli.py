"""Cross-platform command-line interface for BlackHoleMemory (BHM).

Provides a single CLI entry point for macOS, Linux, and Windows to start the
authoritative runtime, check health status, launch Qdrant, and run diagnostic doctor checks.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import subprocess
from pathlib import Path

from .config import settings
from .runtime_storage import resolve_runtime_storage_config, inspect_memory_store_schema
from .tools.infra_healer import tool_check_and_heal_docker, DOCKER_HEALTHY_STATUS

__version__ = "1.8.0"


def _check_health(host: str = "127.0.0.1", port: int = 8000) -> dict[str, object]:
    url = f"http://{host}:{port}/health/ready"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "BHM-CLI"})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return {"online": True, "status_code": resp.status, "data": data}
    except Exception as exc:
        return {"online": False, "error": str(exc)}


def cmd_start(args: argparse.Namespace) -> int:
    """Start the authoritative BHM FastAPI server."""
    host = args.host or settings.host
    port = args.port or settings.port
    print(f"Starting BlackHoleMemory authoritative runtime on http://{host}:{port}...")

    # Set authoritative mode env if not set
    os.environ.setdefault("BHM_MEMORY_STORE_MODE", "sqlite-authoritative")

    import uvicorn
    uvicorn.run(
        "blackholememory.main:app",
        host=host,
        port=port,
        reload=args.reload,
        log_level="info",
    )
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """Check health and readiness of running BHM server."""
    host = args.host or settings.host
    port = args.port or settings.port
    res = _check_health(host, port)
    if res["online"]:
        print(f"[OK] BlackHoleMemory is running at http://{host}:{port}")
        print(json.dumps(res["data"], indent=2, ensure_ascii=False))
        return 0
    else:
        print(f"[OFFLINE] BlackHoleMemory is not reachable at http://{host}:{port}")
        print(f"Detail: {res.get('error')}")
        return 1


def cmd_qdrant_start(args: argparse.Namespace) -> int:
    """Ensure Docker is running and launch Qdrant vector database container."""
    print("Checking Docker status...")
    docker_status = tool_check_and_heal_docker()
    if docker_status != DOCKER_HEALTHY_STATUS:
        print(f"[ERROR] Docker is unavailable: {docker_status}")
        return 1

    print("Starting Qdrant via Docker...")
    cmd = [
        "docker", "run", "-d",
        "--name", "bhm-qdrant",
        "-p", "6333:6333",
        "-p", "6334:6334",
        "-v", "bhm_qdrant_storage:/qdrant/storage",
        "qdrant/qdrant:v1.12.1"
    ]
    try:
        check_proc = subprocess.run(["docker", "ps", "-q", "-f", "name=bhm-qdrant"], capture_output=True, text=True)
        if check_proc.stdout.strip():
            print("[OK] Qdrant container 'bhm-qdrant' is already running.")
            return 0

        check_all = subprocess.run(["docker", "ps", "-a", "-q", "-f", "name=bhm-qdrant"], capture_output=True, text=True)
        if check_all.stdout.strip():
            print("Restarting existing 'bhm-qdrant' container...")
            subprocess.run(["docker", "start", "bhm-qdrant"], check=True)
            print("[OK] Qdrant container restarted.")
            return 0

        subprocess.run(cmd, check=True)
        print("[OK] Qdrant container started successfully on ports 6333/6334.")
        return 0
    except subprocess.CalledProcessError as exc:
        print(f"[ERROR] Failed to start Qdrant container: {exc}")
        return 1


def cmd_doctor(args: argparse.Namespace) -> int:
    """Perform diagnostic health and configuration check."""
    print("=== BlackHoleMemory Doctor Diagnostic ===")
    print(f"OS Platform: {sys.platform}")
    print(f"Python Version: {sys.version.split()[0]}")

    config = resolve_runtime_storage_config()
    print(f"Storage Mode: {config.mode.value}")
    print(f"Database Path: {config.database_path}")
    db_exists = config.database_path.exists()
    print(f"Database Exists: {db_exists}")

    if db_exists:
        valid, schema_reason = inspect_memory_store_schema(config.database_path)
        print(f"Database Schema Status: {'[OK]' if valid else '[WARNING]'} ({schema_reason})")
    else:
        print("Database Schema Status: [PENDING INITIALIZATION]")

    res = _check_health()
    if res["online"]:
        print(f"BHM Server API: [ONLINE] (http://127.0.0.1:8000)")
    else:
        print(f"BHM Server API: [OFFLINE] (http://127.0.0.1:8000)")

    docker_res = tool_check_and_heal_docker()
    print(f"Docker Engine: {'[OK]' if docker_res == DOCKER_HEALTHY_STATUS else '[UNAVAILABLE]'}")

    return 0


def cmd_profile(args: argparse.Namespace) -> int:
    from .context_profiles import load_context_profiles, resolve_context_profile, DEFAULT_CONTEXT_PROFILE
    action = getattr(args, "profile_action", "status") or "status"
    try:
        default_name, profiles = load_context_profiles()
    except Exception as exc:
        print(f"Error loading profiles: {exc}")
        return 1

    if action == "status":
        curr = resolve_context_profile(args.name if hasattr(args, "name") and args.name else None)
        print(f"=== BHM Context Profile Status ===")
        print(f"Active Profile: {curr.name}")
        print(f"Token Budget:   {curr.token_budget}")
        print(f"Max Items:      {curr.limit}")
        print(f"Max Item Chars: {curr.max_item_chars}")
        return 0
    elif action == "set":
        target = getattr(args, "profile_name", "")
        if not target:
            print("Error: profile name is required for 'set'")
            return 1
        try:
            prof = resolve_context_profile(target)
            print(f"[OK] Context profile set to: {prof.name}")
            return 0
        except ValueError as exc:
            print(f"Error: {exc}")
            return 1
    elif action == "compare":
        print(f"=== BHM Context Profiles Comparison ===")
        print(f"{'NAME':<15} {'BUDGET':<10} {'LIMIT':<10} {'MAX_CHARS':<10}")
        print("-" * 48)
        for p_name, p_obj in profiles.items():
            print(f"{p_obj.name:<15} {p_obj.token_budget:<10} {p_obj.limit:<10} {p_obj.max_item_chars:<10}")
        return 0
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="bhm",
        description="BlackHoleMemory (BHM) cross-platform CLI tool",
    )
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    p_start = subparsers.add_parser("start", help="Start BlackHoleMemory server")
    p_start.add_argument("--host", type=str, default="127.0.0.1", help="Host address to bind (default: 127.0.0.1)")
    p_start.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")
    p_start.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    p_start.set_defaults(func=cmd_start)

    p_status = subparsers.add_parser("status", help="Check BlackHoleMemory server status")
    p_status.add_argument("--host", type=str, default="127.0.0.1", help="Host address")
    p_status.add_argument("--port", type=int, default=8000, help="Port number")
    p_status.set_defaults(func=cmd_status)

    p_qdrant = subparsers.add_parser("qdrant", help="Manage Qdrant vector database")
    q_sub = p_qdrant.add_subparsers(dest="qdrant_command", help="Qdrant subcommands")
    q_start = q_sub.add_parser("start", help="Start local Qdrant container")
    q_start.set_defaults(func=cmd_qdrant_start)

    p_doctor = subparsers.add_parser("doctor", help="Run system diagnostics")
    p_doctor.set_defaults(func=cmd_doctor)

    p_profile = subparsers.add_parser("profile", help="Manage BHM context profiles")
    prof_sub = p_profile.add_subparsers(dest="profile_action", help="Profile actions")
    prof_stat = prof_sub.add_parser("status", help="Show current profile status")
    prof_stat.set_defaults(func=cmd_profile)
    prof_set = prof_sub.add_parser("set", help="Set active context profile")
    prof_set.add_argument("profile_name", type=str, help="Profile name (e.g. low-context, standard, deep)")
    prof_set.set_defaults(func=cmd_profile)
    prof_cmp = prof_sub.add_parser("compare", help="Compare all available context profiles")
    prof_cmp.set_defaults(func=cmd_profile)

    args = parser.parse_args()

    if hasattr(args, "func"):
        return args.func(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
