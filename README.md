# CursorMCPWorkspace
Integrates Cursor with an MCP server for BibleScholarProjectv2, a Bible study platform.

## Setup
1. Install: `pip install -r requirements.txt`
2. Configure: Copy `.env.example` to `.env`, update credentials.
3. Start MCP: `python scripts/mcp_server.py`
4. Start project: `cd BibleScholarProjectv2 && ./start_servers.bat`
5. Open in Cursor.

## Structure
- `BibleScholarProjectv2/`: Main project.
- `BibleScholarProjectClean/`: Backup.
- `src/`, `scripts/`: Code and MCP server.
- `.cursor/`: Rules and configs.
- `logs/`: Logs (e.g., `mcp_server.log`).

## MCP Server
- Start: `python scripts/mcp_server.py`
- Tools: `check_ports`, `enforce_etl_guidelines`, `semantic_search`, etc.
- Logs: `logs/mcp_server.log`.

## Testing
- Run tools in chat (e.g., "executeTool check_ports").
- Test project servers: `cd BibleScholarProjectv2 && ./start_servers.bat`.
- Run pytest: `pytest BibleScholarProjectv2/tests/` and `pytest BibleScholarProjectClean/tests/`. 