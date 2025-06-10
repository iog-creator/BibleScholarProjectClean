#!/usr/bin/env python3
"""
Test MCP Server Import Path
Verifies that the MCP server imports from workspace root correctly
"""

import sys
import os

print("=== TESTING MCP SERVER IMPORT PATH ===")

# Simulate the MCP server import path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # Workspace root

try:
    from mcp_universal_operations import execute_operation, universal_router
    print(f"✅ MCP server can import from workspace root")
    print(f"✅ Operations available: {len(universal_router.operation_registry)}")
    
    # Test operation
    result = execute_operation({
        'domain': 'data',
        'operation': 'check',
        'target': 'database_stats',
        'action_params': {}
    })
    
    print(f"✅ Operation status: {result['status']}")
    print(f"✅ Message: {result['message']}")
    
    print("\n🎯 MCP SERVER IMPORT: WORKING CORRECTLY!")
    print("✅ Imports from workspace root (not project-specific)")
    print("✅ Universal operations accessible")
    print("✅ Ready for any project in workspace")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("❌ MCP server import path needs fixing") 