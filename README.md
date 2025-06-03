# CursorMCPWorkspace
Integrates Cursor with an MCP server for BibleScholarProjectv2, a Bible study platform.

## Setup
1. Install: `pip install -r requirements.txt`
2. Configure: Copy `.env.example` to `.env`, update credentials.
3. Start MCP: `python scripts/mcp_server.py`
4. Start project servers: `cd BibleScholarProjectv2 && scripts\start_servers.bat`
5. Open in Cursor.

## Structure
- `BibleScholarProjectv2/`: Main project (all server and management scripts are canonical here).
- `BibleScholarProjectClean/`: Backup (do not modify directly).
- `src/`, `scripts/`: Code and MCP server.
- `.cursor/`: Rules and configs.
- `logs/`: Logs (e.g., `mcp_server.log`).

## MCP Server
- Start: `python scripts/mcp_server.py`
- Tools: `check_ports`, `enforce_etl_guidelines`, `semantic_search`, etc.
- Logs: `logs/mcp_server.log`.

## Project Server Management (BibleScholarProjectv2)
- **Always use scripts in `BibleScholarProjectv2/scripts/` for starting, stopping, and managing servers.**
- Start all servers with statistics and health checks:
  - `cd BibleScholarProjectv2`
  - `scripts\start_servers.bat`
- Stop all servers:
  - `cd BibleScholarProjectv2`
  - `scripts\stop_servers.bat`
- Individual servers:
  - API: `scripts\run_api_server.bat`
  - Web UI: `scripts\run_web_app.bat`
  - Contextual Insights: `scripts\run_contextual_insights.bat`
  - Vector Search Demo: `scripts\run_vector_search.bat`
- **Do not use root-level .bat files for server management.**

## Testing
- Run tools in chat (e.g., "executeTool check_ports").
- Test servers: `cd BibleScholarProjectv2 && scripts\start_servers.bat` or `cd BibleScholarProjectClean && scripts\start_servers.bat`.
- Run pytest: `pytest BibleScholarProjectv2/tests/` and `pytest BibleScholarProjectClean/tests/`.

## Best Practices
- Only modify or run scripts in `BibleScholarProjectv2/scripts/` for server management.
- Keep `BibleScholarProjectClean` pristine; sync only tested changes from v2.
- Check logs in `BibleScholarProjectv2/logs/` for server output and health.
- For rule and documentation updates, see `.cursor/rules/` and `BibleScholarProjectv2/docs/`.

## Automated Tool Call Logging and Rule Generation

- The MCP server (run from the project root) automatically logs every tool call to `logs/interaction.log`.
- For each tool call, an auto-generated rule file is created in `.cursor/rules/automation/` at the workspace root.
- These files provide a reproducible, auditable record of all tool interactions and are required for compliance and debugging.
- The automation process and compliance requirements are fully documented in:
  - `docs/reference/rules/automation_rule_generation.md`
  - `.cursor/rules/automation/README.md`
  - `.cursor/rules/rule_creation_guide.mdc`
  - `.cursor/rules/logging_and_error_handling.mdc`
- Auto-generated rules older than 30 days are automatically pruned daily (see `scripts/mcp_server.py`).

**All changes to automation or logging must be reflected in the above documentation and rules.**

- The vector search demo server runs on port 5150 by default.
- Start it using `BibleScholarProjectv2/scripts/run_vector_search_demo.bat` or `python -m BibleScholarProjectv2.src.utils.vector_search_demo --debug` from the project root. 