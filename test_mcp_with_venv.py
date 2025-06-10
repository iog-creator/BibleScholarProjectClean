#!/usr/bin/env python3
"""
Test MCP Server with Restored Virtual Environment
"""

import subprocess
import sys
import os

print("=== TESTING MCP SERVER WITH RESTORED PYTHON VENV ===")

# Test 1: Check if venv Python can import MCP operations
venv_python = r"BSPclean\Scripts\python.exe"

try:
    result = subprocess.run([
        venv_python, "-c", 
        "from mcp_universal_operations import execute_operation, universal_router; "
        "print(f'✅ Operations: {len(universal_router.operation_registry)}'); "
        "result = execute_operation({'domain': 'data', 'operation': 'check', 'target': 'database_stats', 'action_params': {}}); "
        "print(f'✅ Status: {result[\"status\"]}'); "
        "print(f'✅ Message: {result[\"message\"]}');"
    ], capture_output=True, text=True, cwd=os.getcwd())
    
    if result.returncode == 0:
        print("✅ VENV PYTHON TEST PASSED:")
        print(result.stdout)
    else:
        print("❌ VENV PYTHON TEST FAILED:")
        print(result.stderr)
        
except Exception as e:
    print(f"❌ Error testing venv Python: {e}")

# Test 2: Check MCP configuration
print("\n=== MCP CONFIGURATION ===")
try:
    with open('.cursor/mcp.json', 'r') as f:
        import json
        config = json.load(f)
        python_path = config['mcpServers']['bible-scholar-mcp']['command']
        print(f"✅ MCP Python path: {python_path}")
        
        if os.path.exists(python_path):
            print("✅ Python interpreter exists")
        else:
            print("❌ Python interpreter NOT FOUND")
            
except Exception as e:
    print(f"❌ Error checking MCP config: {e}")

print("\n🎯 NEXT STEP: Restart Cursor to reload MCP server with correct Python environment") 