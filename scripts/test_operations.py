#!/usr/bin/env python3
"""Test MCP operations from scripts directory"""

from mcp_universal_operations import execute_operation

def test_database_stats():
    print("Testing database stats operation...")
    result = execute_operation({
        'domain': 'data',
        'operation': 'check', 
        'target': 'database_stats',
        'action_params': {}
    })
    
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    print(f"Results keys: {list(result.get('results', {}).keys())}")
    print(f"Full result: {result}")

if __name__ == "__main__":
    test_database_stats() 