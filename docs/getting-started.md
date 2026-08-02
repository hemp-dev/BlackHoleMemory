# Быстрый старт BlackHoleMemory

Данное руководство поможет вам установить, настроить и запустить **BlackHoleMemory (BHM)**, а также подключить его к вашему AI-агенту.

---

## 1. Системные требования

- **ОС**: macOS (Apple Silicon / Intel), Linux или Windows 10/11;
- **Python**: версия 3.12 или новее;
- **Менеджер пакетов**: [uv](https://docs.astral.sh/uv/);
- **Контейнеризация**: Docker или Colima с Docker Compose для запуска Qdrant.

---

## 2. Установка по операционным системам

### 🍏 macOS (Apple Silicon / Intel)

1. Установите необходимые утилиты через Homebrew:
   ```bash
   brew install python@3.12 uv docker colima
   colima start  # Если используется Colima вместо Docker Desktop
   ```
2. Клонируйте репозиторий и установите зависимости:
   ```bash
   git clone https://github.com/Efidripy/BlackHoleMemory.git
   cd BlackHoleMemory
   uv sync
   ```

### 🐧 Linux / Unix (Ubuntu, Debian, Fedora, Arch)

1. Установите Python 3.12, Git и Docker Engine:
   ```bash
   # Ubuntu / Debian
   sudo apt update && sudo apt install -y python3.12 python3.12-venv git docker.io
   sudo systemctl enable --now docker
   sudo usermod -aG docker $USER
   ```
2. Установите менеджер пакетов `uv`:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. Клонируйте репозиторий и выполните сборку виртуального окружения:
   ```bash
   git clone https://github.com/Efidripy/BlackHoleMemory.git
   cd BlackHoleMemory
   uv sync
   ```

### 🪟 Windows 10/11 (PowerShell / WSL2)

1. Установите Python 3.12, Docker Desktop (с поддержкой WSL2) и `uv`:
   ```powershell
   # В консоли PowerShell (winget)
   winget install Python.Python.3.12
   winget install astral-sh.uv
   winget install Docker.DockerDesktop
   ```
2. Клонируйте репозиторий и установите проект:
   ```powershell
   git clone https://github.com/Efidripy/BlackHoleMemory.git
   cd BlackHoleMemory
   uv sync
   ```

---

## 3. Запуск сервисов

Вы можете использовать кроссплатформенный CLI `bhm` или нативные скрипты автоматизации.

### Вариант А: Использование CLI `bhm` (Рекомендуется)

1. **Диагностика окружения**:
   ```bash
   uv run bhm doctor
   ```

2. **Запуск векторной базы данных Qdrant**:
   ```bash
   uv run bhm qdrant start
   ```

3. **Запуск сервера BHM**:
   ```bash
   uv run bhm start
   ```

### Вариант Б: Использование нативных скриптов

- **macOS / Linux (POSIX)**:
  ```bash
  ./scripts/start-bhm-authoritative.sh
  ```

- **Windows (PowerShell)**:
  ```powershell
  powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-bhm-authoritative.ps1
  ```

---

## 4. Проверка готовности (Readiness Check)

Убедитесь, что сервер успешно запущен и отвечает по адресу готовности:

```bash
curl http://127.0.0.1:8000/health/ready
```

Ожидаемый ответ:
```json
{
  "status": "ready",
  "storage": "sqlite-authoritative",
  "qdrant": "connected"
}
```

---

## 5. Доступные адреса и сервисы

После успешного запуска доступны следующие компоненты:

- **BHM REST API**: `http://127.0.0.1:8000/bhm/`
- **MCP Endpoint**: `http://127.0.0.1:8000/mcp`
- **Galaxy UI (3D/2D граф)**: `http://127.0.0.1:8000/bhm/galaxy`
- **Qdrant Dashboard**: `http://127.0.0.1:6333/dashboard/`
- **Redoc API Docs**: `http://127.0.0.1:8000/redoc`

---

## 6. Подключение AI-агента

Укажите адрес MCP в конфигурационном файле вашего агента (Claude Desktop, Cursor, Antigravity, Windsurf и др.):

```json
{
  "mcpServers": {
    "bhm": {
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

После этого агент получит доступ ко всем инструментам долговременной памяти `bhm_*`.
