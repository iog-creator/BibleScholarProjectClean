# MCP Server Startup and Restart Consistency

## Overview
This document describes all possible triggers for MCP server startup and restart, how to diagnose repeated restarts, and best practices for running the server in production and development environments.

---

## Startup/Restart Triggers
- **Cold Start:** Initial launch of the server (manual or script).
- **Port Conflict:** Server attempts to start but finds the port in use; triggers port cleanup and retry logic.
- **File Watcher Reload:** Rule or documentation file changes in `.cursor/rules/` trigger a reload of rules (but not a full server restart).
- **Crash/Abnormal Exit:** Unhandled exceptions or process manager restarts.
- **Manual Restart:** User or admin intentionally restarts the process.

---

## Diagnosing Repeated Restarts
1. **Check the Log File:**
   - See `logs/mcp_server.log` for explicit startup reason logs and error traces.
   - Look for repeated port conflict, crash, or reload messages.
2. **Check for Multiple Instances:**
   - Only one MCP server can run on port 8000. Use `netstat -ano | findstr 8000` (Windows) to check for existing processes.
3. **File Watcher Events:**
   - Frequent rule file changes can trigger reloads (see `logs/workspace_setup.log`).
4. **Unhandled Exceptions:**
   - Review stack traces in the log for crash causes.
5. **Process Manager Loops:**
   - If using a process manager (systemd, pm2, Docker), check its logs for restart loops.

---

## Production vs. Development
- **Production:**
  - Run with a process manager (systemd, pm2, Docker) for auto-restart on crash.
  - Monitor `logs/mcp_server.log` for abnormal restarts.
- **Development:**
  - Use `uvicorn` directly or via the provided scripts.
  - Avoid running multiple instances.
  - Use the file watcher for live rule reloads.

---

## Checklist: Verifying Startup/Restart Behavior
- [ ] Log file contains a clear startup reason and timestamp.
- [ ] Port conflict and resolution attempts are logged.
- [ ] File watcher reloads are logged with the correct reason.
- [ ] Abnormal exits/crashes are logged with stack traces.
- [ ] Only one instance runs on port 8000.
- [ ] Documentation and rules are in sync with code.

---

## References
- [Known Issues](../known_issues.md)
- [Logging and Error Handling Rule](../../.cursor/rules/logging_and_error_handling.mdc)
- [Rule Template](../../.cursor/rules/rule_template.mdc) 