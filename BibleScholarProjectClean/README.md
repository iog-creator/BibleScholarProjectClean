# BibleScholarProjectClean

**Canonical, Production-Ready, and Minimal Version**

> **IMPORTANT:**
> - This folder is **not** a backup or mirror of the main project.
> - It contains only the latest, fully working, and well-documented code and documentation.
> - All updates are **incremental and intentional**: only robust, tested, and production-ready enhancements or fixes are included.
> - No experimental, legacy, or troubleshooting code, comments, or documentation are ever included.
> - This is the gold standard for deployment, onboarding, and reference.

## Setup

1. Clone or copy this folder.
2. Install dependencies:
   ```
pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your environment variables.

## Running the API/Web App

1. Set your environment variables (see `.env.example`).
2. Run the web app:
   ```
$env:PYTHONPATH = "src"; python src/web_app.py
   ```
   (On Linux/Mac: `PYTHONPATH=src python src/web_app.py`)

## Project Structure

- `src/` - All Python code (APIs, logic, utils, etc.)
- `templates/` - HTML templates
- `static/` - CSS/JS/static files
- `scripts/` - Utility scripts
- `data/` - Data files
- `docs/` - Documentation

## Notes
- All imports are relative to `src/` (no `src.` prefix in code).
- This project is self-contained and does not depend on v1/v2 folders.
- **This folder is always kept clean and minimal.**
- **No legacy, experimental, or troubleshooting code or docs are present.**
- All documentation is up-to-date and relevant to the current, working state of the code.
- See `docs/` for further documentation and rules.

### Server Management
- **stop_servers.bat**: Stops all servers (API:5000, Web UI:5001, Contextual Insights:5002) by terminating Python processes and verifying ports are free. Logs to `logs\server_management.log`.
- **start_servers.bat**: Starts all servers using wrapper scripts (`scripts/run_api_server.bat`, etc.), checks port availability, and verifies health. Logs to `logs\server_management.log`.
- **Logs**: All server logs are written via batch redirection (see `scripts/run_*.bat`), not Python FileHandler, to avoid permission errors on Windows. Check `logs\server_management.log` and individual server logs (e.g., `logs\web_app.log`) for debugging.
- **Incremental Update Policy**: Only robust, tested, and production-ready changes are included here. No mirroring or backup of experimental code.
- **Troubleshooting**: If a server fails to start, review the corresponding log file in `logs/` for error details.

### Cursor Rules Compliance
- All server management, logging, and documentation changes follow always-on Cursor rules for process management, logging, and incremental clean-folder updates.
- If you update scripts or documentation, ensure the README and clean project are kept in sync.

# BibleScholarProjectClean Documentation

## Clean-Folder Philosophy and Incremental Update Policy

- This folder is the **canonical, production-ready, and minimal version** of the project.
- All updates are **incremental and intentional**: only robust, tested, and well-documented enhancements or fixes are included.
- **No legacy, experimental, or troubleshooting code, comments, or documentation** are ever included.
- Use this folder as the gold standard for deployment, onboarding, and reference.
- If you need to roll back or reference a previous working state, use the history of this folder, not the main project's troubleshooting history.

## Server Management and Troubleshooting (May 2025 Update)

### Contextual Insights API: Decorator Error Resolved
- The `AttributeError: 'dict' object has no attribute 'cached'` was caused by a stale `@cache.cached` decorator in `src/api/contextual_insights_api.py`.
- **Resolution:**
  - All `@cache.cached` decorators were removed from the codebase.
  - All `__pycache__` directories and `.pyc` files must be deleted after such changes to prevent stale code from running.
  - Always restart all servers after clearing caches to ensure the latest code is loaded.

### LM Studio/Language Model Connection
- The Contextual Insights endpoint now works, but requires LM Studio (or compatible language model server) to be running and accessible at the configured address (default: `192.168.1.119:1234`).
- If you see an error like `Error communicating with language model: HTTPConnectionPool...`, ensure LM Studio is running and reachable.
- Update the `LM_STUDIO_API_URL` environment variable if the address or port changes.

### Permanent Fix Process
1. Remove any stale decorators or code.
2. Delete all Python caches:
   ```powershell
   Get-ChildItem -Recurse -Include __pycache__,*.pyc | Remove-Item -Recurse -Force
   ```
3. Stop all servers:
   ```powershell
   .\stop_servers.bat
   ```
4. Start all servers:
   ```powershell
   .\start_servers.bat
   ```
5. Test endpoints and check logs for errors.

### Always-On Rules
- All changes must comply with always-on Cursor rules, including documentation, robust error handling, and incremental clean-folder updates.

## Configuration (Config-Driven Architecture)

All model, embedding, reranker, and feature settings are now managed in `config/config.json` (not in `.env`). This file is validated at runtime using Pydantic. Only secrets (API keys, passwords) and the config path should be in `.env`.

- Edit `config/config.json` to change model, embedding, reranker, or feature settings.
- The config is loaded and validated at startup. If invalid, the server/test suite will halt with a teaching-mode error message.
- See `config/config.json` for structure and examples.

## Skill Tracker Feature

Visit `/skills` in your browser to view your programming skill progress. The feature reads from `user_skills.json` to display XP and level. You can extend this by adding an "Ask LM Studio for Advice" button and backend route to integrate with LM Studio.

## Progress Tracking & Snapshots

The project includes a lightweight progress tracking system using SQLite (`data/progress.db`).

- **Tables**: `users`, `skills`, `points_log`, `snapshots`
- **Seeded Users**: Orchestrator, Logan
- **Seeded Skills**: Python Programming, Terminal/Command Line, AI Orchestration, ...

### API Endpoints
- `POST /progress/award` — Award points to a user for a skill
- `GET /progress?user=...` — Get current points per skill for a user
- `GET /progress/report?user=...&period=week|month|...` — Get a report for a period
- `POST /progress/snapshot` — Take a snapshot for a user/period
- `GET /progress/snapshot?user=...&period=...` — Get the latest snapshot for a user/period

### Implementation Notes
- All DB operations are logged to `logs/progress_tracker.log`.
- Indexing is used for fast lookups.
- Snapshots allow for historical tracking and analytics.

### Testing
- See `tests/test_integration.py` for tests covering points, reports, and snapshots.

_Last updated: 2025-05-28_

---
_Last updated: 2025-05-23_ 