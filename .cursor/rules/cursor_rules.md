# Cursor Rules for CursorMCPWorkspace

- Use MCP tools from `scripts/mcp_server.py` (e.g., `check_ports`, `enforce_etl_guidelines`, `semantic_search`) for tasks.
- Use absolute paths, e.g., `C:/Users/mccoy/Documents/Projects/Projects/CursorMCPWorkspace/BibleScholarProjectv2/src/etl/etl_versification.py`.
- Verify changes for ETL (`etl_versification.py`, line 45) or database tasks (`database.py`, line 23).
- Log to `logs/mcp_server.log`.
- Keep `BibleScholarProjectClean` untouched unless syncing tested changes. 