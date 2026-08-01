# Быстрый старт

## Требования

- macOS (Apple Silicon / Intel), Linux или Windows 10/11;
- Python 3.12+;
- [uv](https://docs.astral.sh/uv/);
- Docker или Colima с Docker Compose для локального Qdrant.

## Установка

```bash
git clone https://github.com/Efidripy/BlackHoleMemory.git
cd BlackHoleMemory
uv sync
```

## Запуск

Вы можете использовать единый CLI `bhm` или нативные скрипты:

### Использование CLI `bhm` (кроссплатформенно)

```bash
# Проверка здоровья системы и зависимостей
uv run bhm doctor

# Запуск локального контейнера Qdrant
uv run bhm qdrant start

# Запуск authoritative сервера BHM runtime
uv run bhm start
```

### Использование нативных скриптов автоматизации

На macOS / Linux (POSIX):

```bash
./scripts/start-bhm-authoritative.sh
```

На Windows (PowerShell):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-bhm-authoritative.ps1
```

### Проверка readiness

```bash
curl http://127.0.0.1:8000/health/ready
```

Основные адреса:

- API: `http://127.0.0.1:8000/bhm/`;
- MCP: `http://127.0.0.1:8000/mcp`;
- Galaxy UI: `http://127.0.0.1:8000/bhm/galaxy`;
- Qdrant dashboard: `http://127.0.0.1:6333/dashboard/`.

Для остановки и диагностики используйте команды `bhm` (`uv run bhm qdrant stop`), штатные команды Docker / Colima и скрипты из `scripts/`. Runtime state не коммитится в Git.
