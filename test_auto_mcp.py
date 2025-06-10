#!/usr/bin/env python3
"""
Test script for AUTO domain MCP operations
Tests automatic rule creation, documentation updates, and holistic system checks
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_universal_operations import execute_operation

def test_auto_operations():
    """Test AUTO domain operations"""
    print("=== TESTING AUTO DOMAIN OPERATIONS ===")
    
    # Test 1: Holistic system check
    print("\n1. Testing holistic system check...")
    try:
        result = execute_operation({
            'domain': 'auto',
            'operation': 'check',
            'target': 'system'
        })
        print(f"✅ Holistic check: {result.get('message', 'Unknown')}")
        if 'data' in result:
            health = result['data'].get('overall_health', 'Unknown')
            print(f"   Overall health: {health}")
            components = result['data'].get('components', {})
            for comp_name, comp_data in components.items():
                status = comp_data.get('status', 'unknown')
                print(f"   {comp_name}: {status}")
    except Exception as e:
        print(f"❌ Holistic check failed: {e}")
    
    # Test 2: Auto rule creation
    print("\n2. Testing automatic rule creation...")
    try:
        result = execute_operation({
            'domain': 'auto',
            'operation': 'create',
            'target': 'rule',
            'description': 'Fixed nested f-string syntax error',
            'component': 'contextual_insights_api',
            'solution': 'Replaced nested f-string with string concatenation'
        })
        print(f"✅ Rule creation: {result.get('message', 'Unknown')}")
        print(f"   Rule created: {result.get('rule_created', False)}")
        if result.get('rule_file'):
            print(f"   Rule file: {result.get('rule_file')}")
    except Exception as e:
        print(f"❌ Rule creation failed: {e}")
    
    # Test 3: Documentation update
    print("\n3. Testing documentation update...")
    try:
        result = execute_operation({
            'domain': 'auto',
            'operation': 'update',
            'target': 'docs',
            'change_type': 'fix_applied',
            'component': 'mcp_server',
            'details': 'Added AUTO domain operations for automatic system management'
        })
        print(f"✅ Documentation update: {result.get('message', 'Unknown')}")
        print(f"   Changes logged: {result.get('changes_logged', 0)}")
    except Exception as e:
        print(f"❌ Documentation update failed: {e}")
    
    # Test 4: Fix and document workflow
    print("\n4. Testing fix and document workflow...")
    try:
        result = execute_operation({
            'domain': 'auto',
            'operation': 'fix',
            'target': 'and_document',
            'description': 'Added AUTO domain to MCP server',
            'component': 'mcp_universal_operations',
            'solution': 'Integrated AutoSystemManager class with automatic rule creation and documentation updates'
        })
        print(f"✅ Fix and document workflow: {result.get('message', 'Unknown')}")
        if 'steps' in result:
            print(f"   Workflow steps completed: {len(result['steps'])}")
    except Exception as e:
        print(f"❌ Fix and document workflow failed: {e}")
    
    # Test 5: Verify and update workflow
    print("\n5. Testing verify and update workflow...")
    try:
        result = execute_operation({
            'domain': 'auto',
            'operation': 'verify',
            'target': 'and_update'
        })
        print(f"✅ Verify and update workflow: {result.get('message', 'Unknown')}")
        if 'verification' in result:
            verification = result['verification']
            health = verification.get('data', {}).get('overall_health', 'Unknown')
            print(f"   System health: {health}")
    except Exception as e:
        print(f"❌ Verify and update workflow failed: {e}")
    
    print("\n=== AUTO DOMAIN TEST COMPLETE ===")

if __name__ == "__main__":
    test_auto_operations() 