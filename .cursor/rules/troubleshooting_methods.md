# Troubleshooting Methods

## Rule: Use Logs for Troubleshooting

**Type**: Always Apply
**Priority**: High

### Core Principle
**ALWAYS prefer logs over terminal output parsing for troubleshooting** - terminal command outputs are unreliable for complex debugging.

### Required Approach
1. **Check log files** instead of relying on terminal output
2. **Read structured log files** like:
   - `logs/api_app.log` - API server operations
   - `logs/mcp_operations/successful_operations.jsonl` - MCP operations
   - `logs/contextual_insights.log` - API processing details
3. **Use log timestamps** to trace issues chronologically
4. **Parse JSON logs** for structured debugging data

### Prohibited Approach
- ❌ Don't rely on terminal command outputs for troubleshooting
- ❌ Don't assume terminal parsing is accurate
- ❌ Don't use complex terminal commands when logs exist

### Implementation
```python
# Good: Read logs for debugging
with open('logs/api_app.log', 'r') as f:
    latest_logs = f.readlines()[-20:]

# Bad: Rely on terminal parsing
result = subprocess.run(['some_command'], capture_output=True)
```

**This rule ensures reliable troubleshooting by using structured log data instead of unpredictable terminal output.** 