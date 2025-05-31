---
description: Enforces robust, repeatable server startup and single source of truth for all development and deployment in BibleScholarProjectv2.
globs:
  - "src/**/*.py"
  - "scripts/*.py"
  - "tests/**/*.py"
  - "start_servers.bat"
  - "README.md"
  - ".env*"
  - ".cursor/rules/standards/server_startup_consistency.md"
type: always
alwaysApply: true
---

> **This rule follows the [Cursor Rules Guide](https://docs.cursor.com/context/rules) for project rules, structure, and enforcement.**

# Server Startup Consistency Rule

## Purpose
To ensure robust, repeatable, and error-free server startup and development for BibleScholarProject, the following must always be enforced:

- **Single Source of Truth:**  
  All code, scripts, and configuration must be run and edited ONLY in the `BibleScholarProjectv2` folder.  
  `BibleScholarProjectClean` is the canonical backup and must always be kept in sync.

- **Startup Process:**  
  1. Kill all Python processes on the primary and fallback ports (8000, 8001, 8002) using `start_mcp_server.bat`.
  2. Start the MCP server with:
     ```bat
     start_mcp_server.bat
     ```
     This script auto-detects the Python executable, sets `PYTHONUTF8=1`, terminates existing processes, cleans logs, and uses `uvicorn scripts.mcp_server:app` on an available port.
  3. Start the other servers as needed:
     - API: `python -m src.api.contextual_insights_api` (`PYTHONPATH=src`)
     - UI: `python web_app.py`
     - Contextual Insights: `python run_contextual_insights_web.py` (if used)
  4. Run health checks (API, UI, LM Studio, DB, inference) and abort startup if any fail.

- **No Legacy or Duplicate Files:**  
  Do not use or edit any files outside `BibleScholarProjectv2`