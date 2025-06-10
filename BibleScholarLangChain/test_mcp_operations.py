#!/usr/bin/env python3
"""
Test script for MCP Universal Operations
"""
import sys
sys.path.insert(0, '.')

from mcp_universal_operations import execute_operation, universal_router

def test_operations():
    print("=== MCP UNIVERSAL OPERATIONS TEST ===")
    print(f"Total operations available: {len(universal_router.operation_registry)}")
    print()
    
    # Test 1: Database stats check
    print("1. Testing database stats check...")
    result = execute_operation({
        'domain': 'data',
        'operation': 'check', 
        'target': 'database_stats',
        'action_params': {}
    })
    print(f"   Status: {result['status']}")
    print(f"   Message: {result['message']}")
    if result['status'] == 'success':
        print(f"   Results keys: {list(result.get('results', {}).keys())}")
    print()
    
    # Test 2: Hebrew word analysis
    print("2. Testing Hebrew word analysis...")
    result = execute_operation({
        'domain': 'data',
        'operation': 'analyze',
        'target': 'hebrew_words',
        'action_params': {'search_term': 'love', 'limit': 5}
    })
    print(f"   Status: {result['status']}")
    print(f"   Message: {result['message']}")
    print()
    
    # Test 3: Port checking
    print("3. Testing port checking...")
    result = execute_operation({
        'domain': 'system',
        'operation': 'check',
        'target': 'ports',
        'action_params': {'ports': [5432, 5000]}
    })
    print(f"   Status: {result['status']}")
    print(f"   Message: {result['message']}")
    print()
    
    # Test 4: Rule enforcement
    print("4. Testing rule enforcement...")
    result = execute_operation({
        'domain': 'rules',
        'operation': 'enforce',
        'target': 'database',
        'action_params': {}
    })
    print(f"   Status: {result['status']}")
    print(f"   Message: {result['message']}")
    print()
    
    print("=== TEST COMPLETED ===")

if __name__ == "__main__":
    test_operations() 