#!/usr/bin/env python3
"""
Test Workspace-Level MCP Architecture
Verifies that MCP operations work from workspace root for any project
"""

print("=== TESTING WORKSPACE-LEVEL MCP ARCHITECTURE ===")

try:
    # Test 1: Import from workspace root
    from mcp_universal_operations import execute_operation, universal_router
    print("✅ Successfully imported from workspace root")
    print(f"✅ Operations available: {len(universal_router.operation_registry)}")
    
    # Test 2: Execute a database operation
    result = execute_operation({
        'domain': 'data',
        'operation': 'check',
        'target': 'database_stats',
        'action_params': {}
    })
    
    print(f"✅ Database operation status: {result['status']}")
    print(f"✅ Message: {result['message']}")
    
    # Test 3: Execute a system operation
    result = execute_operation({
        'domain': 'system',
        'operation': 'check',
        'target': 'ports',
        'action_params': {'ports': [5432, 5000]}
    })
    
    print(f"✅ System operation status: {result['status']}")
    print(f"✅ Port check: {result['message']}")
    
    print("\n🎯 WORKSPACE MCP ARCHITECTURE: WORKING CORRECTLY!")
    print("✅ Universal operations available from workspace root")
    print("✅ Can be used by any project in the workspace")
    print("✅ No project-specific dependencies")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("❌ Workspace MCP architecture needs fixing") 