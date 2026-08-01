# Архитектура BlackHoleMemory (BHM)

BlackHoleMemory (BHM) — локальная изолированная система долговременной памяти для AI-агентов (Codex, Claude, Cursor, Windsurf и др.). Она решает проблему потери контекста между сессиями работы AI, предоставляя детерминированное, поддающееся аудиту и восстанавливаемое хранилище знаний о проекте.

---

## Архитектурные принципы

1. **Local-First & Self-Hosted**: Данные проекта, контекст и ключи хранятся локально на машине оператора. Никакие сырые данные не отправляются во внешние сервисы без явной настройки.
2. **SQLite WAL как единственный источник истины (Authoritative Store)**: Все события, записи памяти, графы, чекпоинты и метаданные фиксируются в SQLite базы данных в режиме Write-Ahead Logging (WAL).
3. **Восстанавливаемые векторные проекции (Qdrant Vector Projections)**: Индекс Qdrant используется исключительно для семантического поиска и векторных проекций. При сбое или очистке векторного индекса проекция может быть полностью перестроена на основе SQLite WAL.
4. **Принцип безопасности Proposal-Only**: Любые операции изменения кода или структуры проекта генерируют предложения (proposals), а не применяют изменения автоматически. Деструктивные действия требуют явного подтверждения оператором.
5. **Streamable HTTP MCP Endpoint**: Поддержка протокола Model Context Protocol (MCP) через локальный HTTP-эндпоинт (`http://127.0.0.1:8000/mcp`), что обеспечивает работу с любыми современными AI-агентами.

---

## Высокоуровневая диаграмма компонентов

```text
+-------------------------------------------------------------------+
|                            AI Agent                               |
|               (Codex, Claude, Cursor, Windsurf)                   |
+-------------------------------------------------------------------+
                                  |
                   MCP (HTTP) / REST API / CLI
                                  |
                                  v
+-------------------------------------------------------------------+
|                        FastAPI Runtime                            |
|  - MCP Server (bhm_mcp.py, Streamable HTTP)                       |
|  - REST Endpoints (/bhm/*, /health/*)                             |
|  - Galaxy UI (/bhm/galaxy)                                        |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                      Orchestration & Logic                        |
|  - LangGraph (Stateful Flows & Agent Loops)                       |
|  - Mem0 Adapter (Semantic & Logical Layer)                        |
|  - Context Compiler & Fusion Engine                               |
|  - Code Graph & Repository Intelligence                           |
+-------------------------------------------------------------------+
         |                                           |
         v                                           v
+------------------------+                 +------------------------+
|   SQLite WAL Store     |  ---rebuild---> |  Qdrant Vector DB      |
| (Authoritative Master) |                 | (Recoverable Index)    |
+------------------------+                 +------------------------+
```

---

## Ключевые компоненты системы

### 1. Authoritative Storage (SQLite WAL)
- Модули: `memory_repository.py`, `storage_state.py`, `runtime_storage.py`.
- Хранит историю изменений, полные тексты записей памяти, сущности графа кода, чекпоинты, ADR и журналы вызовов.
- Гарантирует ACID-транзакционность и локальную надежность.

### 2. Semantic Layer (Mem0 Integration)
- Модули: `mem0_adapter.py`, `memory_foundry.py`, `memory_graph.py`.
- Предоставляет семантическое извлечение фактов, связывание концептов и категориальный поиск по типам знаний (`convention`, `architecture`, `decision`, `task`, `bug_fix`).

### 3. Vector Projection (Qdrant)
- Модули: `qdrant_projector.py`, `qdrant_catalog.py`, `qdrant_lifecycle.py`, `qdrant_retention.py`.
- Служит ускорителем для векторного ранжирования (k-NN).
- Содержит отпечатки для быстрого семантического поиска. Состояние проекции отслеживается через `bhm_reconcile_projection.py`.

### 4. Code Graph & Repository Intelligence
- Модули: `code_graph.py`, `repository_index.py`, `change_impact.py`, `bicep_parser.py` и др.
- Строит граф связей кода (импорты, вызовы функций, зависимости типов, модули IaC) и рассчитывает Change Impact (риск и влияние изменений на другие компоненты).

### 5. Multi-Agent & LLM Governance
- Модули: `llm_gateway.py`, `llm_safety.py`, `llm_delegation_policy.py`, `llm_resource_governor.py`.
- Контролирует использование ресурсов LLM, кэширование ответов, политики безопасности и разграничения доступа для субагентов.

### 6. MCP Protocol & Surfaces
- Модули: `bhm_mcp.py`, `mcp_streamable_http.py`, `mcp_doctor.py`, `mcp_panel.py`.
- Реализует стандартизированный MCP-сервер поверх Streamable HTTP для бесшовного подключения агентов.

---

## Границы безопасности и изоляция (Trust Boundaries)

1. **Local Security Gate (`local_security_gate.py`)**: Каждая поступающая запись или операция проверяется на наличие чувствительных секретов (API-ключи, токены, пароли) до сохранения в SQLite или отправки в векторную базу.
2. **Изоляция проектов (Project Isolation)**: Записи памяти и векторы тегируются строгим идентификатором проекта (`project_id`). Поиск и извлечение ограничены текущим контекстом проекта.
3. **Proposal Safety**: Операции изменения файла или структуры кода генерируют диффы и планы для одобрения оператором.

---

## Восстановление и самоисправление (Self-Healing & Parity)

BHM содержит встроенный механизм контроля целостности:
- **Projection Reconciliation**: Автоматически обнаруживает осиротевшие или пропущенные векторы в Qdrant и синхронизирует их с SQLite WAL master.
- **Doctor & Health Checks**: Системный CLI (`bhm doctor`) проверяет целостность схемы SQLite, доступность Qdrant и Docker Engine.
