# Заметки к релизу BlackHoleMemory v1.8.0

Релиз **BlackHoleMemory v1.8.0** приносит существенные улучшения в кроссплатформенную совместимость, стабильность работы MCP-интерфейса и расширение графа кода.

---

## Основные изменения и новшества

### 1. Кроссплатформенный CLI `bhm`
- Добавлен единый консольный интерфейс `bhm` (`src/blackholememory/cli.py`) с командами `start`, `status`, `qdrant start` и `doctor`.
- Утилита `bhm doctor` выполняет автоматическую проверку целостности SQLite WAL, состояния Docker и API-эндпоинта.

### 2. Поддержка Streamable HTTP MCP
- Полная адаптация сервера MCP под спецификацию Streamable HTTP (`http://127.0.0.1:8000/mcp`).
- Улучшена совместимость с Cursor, Claude Desktop, Antigravity и Windsurf.

### 3. Расширенный граф кода и IaC
- Добавлены новые парсеры и анализаторы графа кода для конфигураций Terraform, Bicep, Kconfig, Devicetree, Starlark/Bazel и Docker Compose / Kustomize.
- Расширен расчет Change Impact Risk и отслеживание цепочек импорта типов.

### 4. Автоматическая сверка и самоисправление проекций Qdrant
- Внедрены новые алгоритмы синхронизации `bhm_reconcile_projection` для устранения рассинхронизаций между SQLite master и Qdrant.

---

## Инструкции по обновлению

```bash
git pull origin main
uv sync
uv run bhm doctor
```
