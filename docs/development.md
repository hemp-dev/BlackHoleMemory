# Руководство для разработчиков BlackHoleMemory

Данное руководство содержит информацию по настройке окружения разработки, запуску тестов, проверке стиля кода и сборке релизов проекта **BlackHoleMemory**.

---

## 1. Настройка окружения разработки

Проект использует менеджер пакетов `uv`.

```bash
# Клонирование репозитория
git clone https://github.com/Efidripy/BlackHoleMemory.git
cd BlackHoleMemory

# Установка всех зависимостей, включая группы dev, test и build
uv sync --all-extras
```

---

## 2. Запуск тестов

Тестовая сюита построена на `pytest`. Все тесты располагаются в директории `tests/`.

### Запуск всех тестов:
```bash
uv run pytest
```

### Запуск с отчетом о покрытии кода (coverage):
```bash
uv run pytest --cov=blackholememory
```

### Запуск конкретных маркеров:
```bash
# Тесты хранилища
uv run pytest -m bhm_storage

# Тесты MCP-интерфейса
uv run pytest -m bhm_mcp

# Тесты графа кода
uv run pytest -m bhm_graph_ui
```

---

## 3. Проверка качества и стиля кода

В качестве линтера и форматировщика используется `ruff`:

```bash
# Проверка стиля кода
uv run ruff check .

# Автоматическое исправление простых замечаний
uv run ruff check --fix .
```

---

## 4. Запуск бенчмарков

Для проверки производительности извлечения контекста и графа кода используйте скрипт Value Benchmark:

```bash
python scripts/run-bhm-value-benchmark.py
```

Подробная методика и описание условий тестирования находятся в документе [Value Benchmark methodology](benchmarks/bhm-value-benchmark.md).

---

## 5. Сборка автономного релиза (PyInstaller)

Для создания автономного исполняемого пакета (standalone release binary):

### POSIX (macOS / Linux):
```bash
./scripts/build-release.sh
```

### Windows (PowerShell):
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\build-release.ps1
```

Сборка использует спецификацию PyInstaller: `BHM_Launcher.spec`.
