## Log File Locking Rule

- The startup script checks if log files are locked by trying to open them for writing. If 'LOCKED' is shown, it means the server is running and writing to the log.
- This is normal on Windows and does not prevent reading the log for debugging.
- For more details, see [../known_issues.md](../known_issues.md) and `.cursor/rules/logging_and_error_handling.mdc`.

## MCP Python-Based Rule Enforcement

- Rule enforcement is now automated via the Python script `scripts/enforce_all_rules.py`.
- Run the script with:
  ```bash
  python scripts/enforce_all_rules.py
  ```
- By default, the script:
  - Queries the MCP server for all `enforce_rule_*` offerings.
  - Calls each HTTP endpoint `/rules/enforce/{rule_name}`.
  - Prints JSON-formatted results for each rule.
- This approach avoids PowerShell quoting issues and is cross-platform.
- See `scripts/enforce_all_rules.py` and the [README.md](../../README.md#automating-rule-enforcement) for details and customization.

> **Note:** The MCP server runs on port 8000 (Python only). Only one instance can run at a time. If port 8000 is in use, the server will print a message and exit—this is intentional, not a bug. Use `python scripts/enforce_all_rules.py` for rule enforcement. See `start_mcp_server.bat` and `README.md` for details. 