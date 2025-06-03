# Cursor Rules for CursorMCPWorkspace

- Use MCP tools from `scripts/mcp_server.py` (e.g., `check_ports`, `enforce_etl_guidelines`, `semantic_search`) for tasks.
- Use absolute paths, e.g., `C:/Users/mccoy/Documents/Projects/Projects/CursorMCPWorkspace/BibleScholarProjectv2/src/etl/etl_versification.py`.
- Verify changes for ETL (`etl_versification.py`, line 45) or database tasks (`database.py`, line 23).
- Log to `logs/mcp_server.log`.
- Keep `BibleScholarProjectClean` untouched unless syncing tested changes.
- Query MCP server for project context (e.g., `run_query` for database state, `get_file_context` for code) before responding.
- Log interactions to `logs/interaction.log` and generate rules in `.cursor/rules/automation/`.
- Batch tool calls (e.g., combine `verify_data` and `enforce_etl_guidelines`) to optimize performance.
- Prune outdated automation rules (>30 days) with backups in `.mdc` files. 