# BlackHoleMemory

Local self-hosted memory for AI agents.

[English](README.md) | [Русский](README_RU.md)

BlackHoleMemory persists project context across sessions for Codex, Claude, and
other tools, returning it via REST and MCP. The primary use case is Windows,
local infrastructure, and full operator control over data.

## Overview

BlackHoleMemory combines:

- SQLite WAL as the single source of truth for lifecycle and metadata;
- Mem0 as a semantic/logical layer;
- Qdrant as a recoverable vector projection;
- LangGraph for orchestration and stateful agent flows;
- FastAPI and Streamable HTTP MCP for tool and agent integration.

## Why

Standard AI agents lose working context after a session finishes. BHM adds
long-term memory that can be searched, audited, and restored without needing
a second authoritative store.

Key features:

- Local-first and self-hosted deployment;
- SQLite remains authoritative, while Qdrant vector projections can be rebuilt;
- Destructive actions require explicit operator control;
- MCP operates via a local Streamable HTTP endpoint;
- Proposal-only operations do not modify code or data without an explicit apply step.

## Architecture & How It Works

```text
AI agent
   |
   v
REST / MCP
   |
   v
FastAPI + LangGraph
   |
   v
SQLite WAL  ----->  Mem0 semantic layer
   |
   +------------->  Qdrant vector projection
```

## Benchmark

`BHM Value Benchmark v1` compares six modes across 1,000 unique memory/code-intelligence cases repeated 10 times, for a total of 10,000 case evaluations.

| Mode | Task success | Recall@5 | Citation validity | Leakage | Context tokens |
| --- | ---: | ---: | ---: | ---: | ---: |
| `no-memory` | 0.0% | 0.0% | 0.0% | 0 | 0.0 |
| `file-only` | 0.0% | 100.0% | 80.0% | 3000 | 158.1 |
| `naive-vector` | 0.0% | 87.5% | 80.0% | 3000 | 160.5 |
| `bhm-no-graph` | 75.0% | 100.0% | 100.0% | 0 | 89.9 |
| `bhm-no-filters` | 0.0% | 100.0% | 80.0% | 3000 | 158.1 |
| `bhm-full` | 87.5% | 100.0% | 100.0% | 0 | 89.9 |

On a frozen local fixture, BHM does not simply locate the target in top-5: it retains project scope, provenance, and bounded context. Without the graph channel, task success drops to 75%; without safety filtering, it drops to 0% with 3,000 leakages. This is a `deterministic-local-replay`, not real-user telemetry or a universal model benchmark.

[Methodology and full benchmark receipt](docs/benchmarks/bhm-value-benchmark.md)

For a separate check of real model calls, `local-model-replay` is available: 1,000 unique cases × 10 repeats for `file-only` and `bhm-full` (20,000 calls), with fixed prompts, `temperature=0`, `max_tokens=96`, and `tool_budget=0`. The model receives a frozen context and does not call BHM tools; this is not real-user telemetry.
In this release receipt, local-model replay is excluded as the run was not completed and cannot be claimed as a finalized measurement. The contract and reproducible command are preserved in the [benchmark methodology](docs/benchmarks/bhm-value-benchmark.md).

Canonical local MCP endpoint:

```text
http://127.0.0.1:8000/mcp
```

## Installation

BlackHoleMemory supports **macOS**, **Linux / Unix**, and **Windows 10/11**.

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (fast Python package manager)
- Docker or Colima with Docker Compose (for local Qdrant container)

---

### 🍏 macOS (Apple Silicon / Intel)

1. Install dependencies via Homebrew:
   ```bash
   brew install python@3.12 uv docker colima
   colima start  # If using Colima instead of Docker Desktop
   ```
2. Clone repository and install dependencies:
   ```bash
   git clone https://github.com/Efidripy/BlackHoleMemory.git
   cd BlackHoleMemory
   uv sync
   ```

---

### 🐧 Linux / Unix (Ubuntu, Debian, Fedora, Arch)

1. Install Python 3.12, Git, and Docker Engine:
   ```bash
   # Ubuntu / Debian
   sudo apt update && sudo apt install -y python3.12 python3.12-venv git docker.io
   sudo systemctl enable --now docker
   sudo usermod -aG docker $USER
   ```
2. Install `uv`:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. Clone repository and install dependencies:
   ```bash
   git clone https://github.com/Efidripy/BlackHoleMemory.git
   cd BlackHoleMemory
   uv sync
   ```

---

### 🪟 Windows 10/11 (PowerShell / WSL2)

1. Install Python 3.12, Docker Desktop (WSL2 backend), and `uv`:
   ```powershell
   # Via winget in PowerShell
   winget install Python.Python.3.12
   winget install astral-sh.uv
   winget install Docker.DockerDesktop
   ```
2. Clone repository and install dependencies:
   ```powershell
   git clone https://github.com/Efidripy/BlackHoleMemory.git
   cd BlackHoleMemory
   uv sync
   ```

---

## Getting Started

You can use the unified `bhm` CLI or native scripts:

### Using the `bhm` CLI (Cross-Platform)

```bash
# Check system health & dependencies
uv run bhm doctor

# Inspect & compare context profiles
uv run bhm profile status
uv run bhm profile compare

# Start local Qdrant container
uv run bhm qdrant start

# Start authoritative BHM runtime server
uv run bhm start
```

### Using Native Automation Scripts

On macOS / Linux (POSIX):

```bash
# Start BHM authoritative server
./scripts/start-bhm-authoritative.sh

# Build standalone release executable
./scripts/build-release.sh
```

On Windows (PowerShell):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-bhm-authoritative.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\build-release.ps1
```

Verify readiness:

```bash
curl http://127.0.0.1:8000/health/ready
```

Once running, the following endpoints are available:

- BHM API: `http://127.0.0.1:8000/bhm/`;
- MCP: `http://127.0.0.1:8000/mcp`;
- Galaxy UI: `http://127.0.0.1:8000/bhm/galaxy`;
- Qdrant dashboard: `http://127.0.0.1:6333/dashboard/`.

## Documentation

Full project documentation is available in the [`docs/`](docs/README.md) directory:

- **[Getting Started](docs/getting-started.md)** — Installation, execution, and agent setup.
- **[Architecture](docs/architecture.md)** — SQLite WAL, Qdrant, Mem0, and LangGraph architecture.
- **[MCP Tools Reference](docs/mcp-tools.md)** — Reference guide for 50+ BHM MCP tools.
- **[REST API Reference](docs/api-reference.md)** — API endpoints, Galaxy UI, and OpenAPI specs.
- **[CLI & Scripts](docs/cli-reference.md)** — Unified `bhm` CLI and platform automation scripts.
- **[Configuration](docs/configuration.md)** — Settings, environment variables, and manifests.
- **[Development](docs/development.md)** — Testing with pytest, benchmarks, and release builds.
- **[Troubleshooting](docs/troubleshooting.md)** — Diagnostic checks with `bhm doctor` and recovery.

## Acknowledgments

Special thanks to the authors and communities of [LangGraph](https://github.com/langchain-ai/langgraph),
[Mem0](https://github.com/mem0ai/mem0), [Qdrant](https://github.com/qdrant/qdrant),
[FastAPI](https://github.com/fastapi/fastapi), and [MCP](https://modelcontextprotocol.io/).

Extra thanks to everyone who shared ideas, asked tough questions, and helped bring the architecture to a production-ready state.

## License

[0BSD](LICENSE).
