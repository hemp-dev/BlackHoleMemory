# Диагностика

1. Проверьте здоровье системы и зависимости через CLI:

   ```bash
   uv run bhm doctor
   ```

2. Проверьте readiness endpoint:

   ```bash
   curl http://127.0.0.1:8000/health/ready
   ```

3. Если endpoint недоступен:
   - убедитесь, что Qdrant запущен: `uv run bhm qdrant start` или через Docker/Colima;
   - запустите authoritative runtime с помощью `uv run bhm start` или нативного скрипта (`./scripts/start-bhm-authoritative.sh` / `.\scripts\start-bhm-authoritative.ps1`).

4. Если MCP не подключается, проверьте адрес `http://127.0.0.1:8000/mcp` и
   имя сервера `bhm`.

5. Не переносите в Git диагностические логи и raw receipts. Их место — в
   локальной `.local/`-зоне.

Если проблема воспроизводится после чистой установки, приложите версию,
команду запуска и обезличенный ответ readiness; секреты и полные payload не
прикладывайте.
