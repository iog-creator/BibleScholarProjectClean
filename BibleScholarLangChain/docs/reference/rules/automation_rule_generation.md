# Automation of Rule Generation and Logging for Tool Calls

## Overview
This document describes the automated process for logging tool calls and generating rule files in the BibleScholarProjectv2 MCP server environment. It covers the directory structure, standards, compliance requirements, and troubleshooting steps.

---

## How Automation Works
- **Every tool call** made via the MCP server is logged in `logs/interaction.log`.
- **Auto-generated rule files** are created in `.cursor/rules/automation/` at the workspace root. Each file records the tool name, parameters, and result.
- The automation ensures that all tool interactions are reproducible, auditable, and can be referenced for compliance or debugging.

---

## Directory Structure
- `logs/interaction.log`: JSONL log of all tool calls and results.
- `.cursor/rules/automation/`: Contains auto-generated rule files for each tool call.
- `BibleScholarProjectv2/.cursor/rules/`: Main directory for project rules (manual and managed).

---

## Rule and Standards Compliance
- **Logging and Error Handling**: Follows `logging_and_error_handling.mdc` (robust logging, error handling, and stack traces).
- **Rule Creation Guide**: Auto-generated rules use the required YAML frontmatter and structure (see `rule_creation_guide.mdc`).
- **Server Startup Consistency**: All changes require a server restart to take effect (see `standards/server_startup_consistency.md`).
- **Always-on Rules**: All always-on and standards rules are enforced for every tool call and rule file.
- **README**: The process and file locations are consistent with project documentation.

---

## Troubleshooting
- If logs or rule files are not being written:
  - Ensure the MCP server has been restarted after code changes.
  - Check `logs/mcp_server.log` for errors (e.g., serialization issues).
  - Confirm the automation directory exists at `.cursor/rules/automation/`.
  - Verify file permissions and that no process is locking the log files (see `logging_and_error_handling.mdc`).
- If auto-generated rules appear in the wrong location, update the path in the server code and restart.

---

## Best Practices
- Only use scripts in `BibleScholarProjectv2/scripts/` for server management.
- Keep `BibleScholarProjectClean` pristine; sync only tested changes from v2.
- Review and update rules and documentation as the project evolves.
- Reference the [Cursor Rules Guide](https://docs.cursor.com/context/rules) for rule structure and update process.

---

## Rule Pruning & Retention
- Auto-generated rule files older than 30 days are pruned daily by the MCP server.
- Pruned rules are backed up in the same file under a `# Backup (ignore unless restore needed)` section.
- See `scripts/mcp_server.py` for the pruning schedule implementation.

---

## References
- `.cursor/rules/rule_creation_guide.mdc`
- `.cursor/rules/logging_and_error_handling.mdc`
- `.cursor/rules/standards/server_startup_consistency.md`
- `README.md` 