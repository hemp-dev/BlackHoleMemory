# Справочник CLI и скриптов автоматизации BlackHoleMemory

BlackHoleMemory предоставляет единый кроссплатформенный интерфейс командной строки `bhm` (для macOS, Linux и Windows), а также набор вспомогательных скриптов автоматизации.

---

## 1. Единый CLI `bhm`

Утилита `bhm` доступна при установке пакета или через `uv run bhm`.

```bash
uv run bhm --help
```

### Команды CLI

#### `bhm doctor`
Запускает полную диагностику системы, окружения и компонентов:
- Версия Python и платформа ОС;
- Режим хранилища и путь к SQLite базе данных;
- Проверка схемы базы данных;
- Доступность API-сервера BHM (`http://127.0.0.1:8000`);
- Статус Docker Engine и контейнера Qdrant.

Пример использования:
```bash
uv run bhm doctor
```

#### `bhm start`
Запускает authoritative FastAPI сервер BHM.
```bash
# Запуск с параметрами по умолчанию (127.0.0.1:8000)
uv run bhm start

# Запуск на другом хосту и порту с автоперезагрузкой при изменении кода
uv run bhm start --host 0.0.0.0 --port 8080 --reload
```

#### `bhm status`
Проверяет готовность сервера по адресу `/health/ready`.
```bash
uv run bhm status
```

#### `bhm qdrant start`
Проверяет работоспособность Docker Engine и запускает контейнер `bhm-qdrant` (Qdrant v1.12.1) на портах 6333/6334.
```bash
uv run bhm qdrant start
```

---

## 2. Нативные скрипты автоматизации (`scripts/`)

Для развертывания и обслуживания в проекте доступны скрипты под POSIX (macOS/Linux) и Windows (PowerShell):

### POSIX Shell (macOS / Linux)

- **`./scripts/start-bhm-authoritative.sh`**
  Запускает локальный Qdrant (через Docker/Colima) и сервер BHM в authoritative режиме.
- **`./scripts/build-release.sh`**
  Собирает релизный бинарный пакет приложения.
- **`./scripts/start-qdrant.sh`**
  Запуск фонового контейнера Qdrant.

### Windows PowerShell

- **`.\scripts\start-bhm-authoritative.ps1`**
  Полноценный запуск BHM в режиме выполнения PowerShell без профиля:
  ```powershell
  powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-bhm-authoritative.ps1
  ```
- **`.\scripts\build-release.ps1`**
  Сборка автономного исполняемого файла (`.exe`) с помощью PyInstaller и спецификации `BHM_Launcher.spec`.

---

## 3. Вспомогательные утилиты обслуживания

* **`scripts/requeue-bhm-dead-letters.py`**: Повторная отправка сообщений из мертвой очереди (dead-letter queue).
* **`scripts/bhm_vacuum.py`**: Очистка и оптимизация файла базы данных SQLite.
* **`scripts/bhm_reconcile_projection.py`**: Пересчет и сверка векторных проекций Qdrant с SQLite WAL.
