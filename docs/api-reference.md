# Справочник REST API BlackHoleMemory

BlackHoleMemory предоставляет REST API на базе FastAPI. API используется для проверки состояния, визуализации графов в интерфейсе Galaxy UI, управления обучением LLM, выполнения запросов к графу кода и интеграции со сторонними инструментами.

Базовый URL сервера: `http://127.0.0.1:8000`

---

## 1. Проверка состояния и диагностика (Health & Readiness)

### `GET /health/ready`
Проверка полной готовности сервиса к работе (включая SQLite WAL и векторный слой Qdrant).
* **Ответ**: `200 OK`
* **Тело ответа**:
  ```json
  {
    "status": "ready",
    "storage": "sqlite-authoritative",
    "qdrant": "connected"
  }
  ```

### `GET /health/live`
Liveness-проба для контейнеров и оркестраторов.
* **Ответ**: `200 OK` (`{"status": "live"}`)

### `GET /health/dependencies`
Детальный отчет о доступности зависимостей (SQLite, Qdrant, Docker, LLM Gateway).

### `GET /bhm/health`
Внутренний статус подсистем BlackHoleMemory.

---

## 2. Веб-интерфейс Galaxy (Galaxy UI)

### `GET /bhm/galaxy`
Интерактивный веб-интерфейс для 3D/2D визуализации памяти, связей концептов, графа кода и текущего состояния проекта.
* **Доступ**: Открыть в браузере `http://127.0.0.1:8000/bhm/galaxy`

---

## 3. Граф кода и аналитика изменений (Code Graph & Change Impact)

### `POST /bhm/code-graph/query`
Выполнение структуры запросов к графу кода проекта.
* **Тело запроса**:
  ```json
  {
    "project_id": "my-project",
    "query": "find_dependents",
    "target_symbol": "MemoryRepository"
  }
  ```

### `POST /bhm/change-impact/preview`
Анализ рисков и зоны влияния при модификации файлов или символов.
* **Тело запроса**:
  ```json
  {
    "project_id": "my-project",
    "changed_files": ["src/blackholememory/memory_repository.py"]
  }
  ```

---

## 4. LLM Governance, Обучение и Фабрики

### `GET /bhm/llm/capabilities`
Получить список доступных моделей LLM, лимитов и текущих профилей маршрутизации.

### `POST /bhm/llm/policy/decide`
Запросить решение политики безопасного делегирования задач между LLM-моделями.

### `POST /bhm/llm/memory-foundry/preview`
Предварительный просмотр извлечения и синтеза знаний из необработанных сессий или логов.

### `POST /bhm/llm/documentation-factory/preview`
Автоматическая генерация или обновление документации по состоянию графа кода.

---

## 5. Документация OpenAPI & Redoc

Встроенная интерактивная спецификация доступна по следующим адресам:
* **OpenAPI JSON**: `http://127.0.0.1:8000/openapi.json`
* **Redoc UI**: `http://127.0.0.1:8000/redoc`
