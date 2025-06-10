#!/usr/bin/env python3
"""
DAMAGE ASSESSMENT: Working Outside Virtual Environment
Checking for issues caused by working outside BSPclean venv
"""

import sys
import os
import subprocess

print("=== DAMAGE ASSESSMENT: WORKING OUTSIDE VENV ===")
print(f"Current Python: {sys.executable}")
print(f"Current working directory: {os.getcwd()}")

# Check 1: Verify we're in the right venv
if "BSPclean" in sys.executable:
    print("✅ NOW in BSPclean virtual environment")
else:
    print("❌ STILL NOT in BSPclean virtual environment")

# Check 2: Test MCP operations
try:
    from mcp_universal_operations import execute_operation, universal_router
    print(f"✅ MCP operations loaded: {len(universal_router.operation_registry)} operations")
    
    # Test a database operation
    result = execute_operation({
        'domain': 'data',
        'operation': 'check',
        'target': 'database_stats',
        'action_params': {}
    })
    
    print(f"✅ Database operation status: {result['status']}")
    print(f"✅ Message: {result['message']}")
    
    # Check if we have the full implementation (not simplified)
    if 'detailed_stats' in result.get('results', {}):
        print("✅ Full database implementation active")
    else:
        print("❌ Simplified implementation detected - possible venv issue")
        
except Exception as e:
    print(f"❌ MCP operations error: {e}")

# Check 3: Test database connectivity  
try:
    result = execute_operation({
        'domain': 'system',
        'operation': 'check',
        'target': 'ports',
        'action_params': {'ports': [5432, 5000]}
    })
    print(f"✅ Port check: {result['status']}")
except Exception as e:
    print(f"❌ Port check error: {e}")

# Check 4: Verify required packages
try:
    import psycopg
    import langchain
    import dspy
    print("✅ Core packages available: psycopg, langchain, dspy")
except ImportError as e:
    print(f"❌ Missing packages: {e}")

# Check 5: Check for any incorrect __pycache__ or .pyc files
print("\n=== CHECKING FOR CACHE ISSUES ===")
cache_dirs = []
for root, dirs, files in os.walk('.'):
    if '__pycache__' in dirs:
        cache_dirs.append(os.path.join(root, '__pycache__'))

if cache_dirs:
    print(f"❌ Found {len(cache_dirs)} __pycache__ directories that may have wrong Python version")
    for cache_dir in cache_dirs[:5]:  # Show first 5
        print(f"   - {cache_dir}")
else:
    print("✅ No problematic cache directories found")

print("\n=== RECOMMENDATIONS ===")
print("1. Clear all __pycache__ directories to force recompilation in correct venv")
print("2. Restart Cursor to reload MCP server with BSPclean Python")
print("3. Always activate BSPclean venv before any Python operations")
print("4. Update workspace rules to require venv activation") 