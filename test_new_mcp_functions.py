#!/usr/bin/env python3
"""
Test script for new MCP functions
Tests the direct entry functions added to mcp_universal_operations.py
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.abspath('.'))

def test_new_mcp_functions():
    """Test all the new direct entry MCP functions"""
    print("=" * 60)
    print("TESTING NEW MCP DIRECT ENTRY FUNCTIONS")
    print("=" * 60)
    
    try:
        # Import the new functions
        from mcp_universal_operations import (
            get_system_instructions, 
            get_operation_help,
            quick_database_check,
            quick_server_status,
            help_mcp,
            db_check,
            server_status
        )
        print("✅ Successfully imported new MCP functions")
        
        # Test 1: System Instructions
        print("\n1. Testing get_system_instructions()...")
        try:
            result = get_system_instructions()
            print(f"   Status: {result.get('status', 'unknown')}")
            print(f"   Categories: {len(result.get('quick_functions', {}))}")
            print("   ✅ get_system_instructions() works")
        except Exception as e:
            print(f"   ❌ get_system_instructions() failed: {e}")
        
        # Test 2: Help function
        print("\n2. Testing help_mcp()...")
        try:
            result = help_mcp()
            print(f"   Status: {result.get('status', 'unknown')}")
            print("   ✅ help_mcp() works")
        except Exception as e:
            print(f"   ❌ help_mcp() failed: {e}")
        
        # Test 3: Operation help
        print("\n3. Testing get_operation_help('quick_database_check')...")
        try:
            result = get_operation_help('quick_database_check')
            print(f"   Status: {result.get('status', 'unknown')}")
            if result.get('status') == 'success':
                print(f"   Operation: {result.get('operation')}")
                print(f"   Description: {result.get('help', {}).get('description', 'N/A')}")
            print("   ✅ get_operation_help() works")
        except Exception as e:
            print(f"   ❌ get_operation_help() failed: {e}")
        
        # Test 4: Database check (may fail if DB not running)
        print("\n4. Testing quick_database_check()...")
        try:
            result = quick_database_check()
            print(f"   Status: {result.get('status', 'unknown')}")
            print(f"   Message: {result.get('message', 'No message')[:100]}...")
            print("   ✅ quick_database_check() executed (check status for DB connectivity)")
        except Exception as e:
            print(f"   ❌ quick_database_check() failed: {e}")
        
        # Test 5: Server status (may fail if servers not running)
        print("\n5. Testing quick_server_status()...")
        try:
            result = quick_server_status()
            print(f"   Status: {result.get('status', 'unknown')}")
            print(f"   Message: {result.get('message', 'No message')[:100]}...")
            print("   ✅ quick_server_status() executed (check status for server connectivity)")
        except Exception as e:
            print(f"   ❌ quick_server_status() failed: {e}")
        
        # Test 6: Aliases
        print("\n6. Testing aliases (db_check, server_status)...")
        try:
            db_result = db_check()
            server_result = server_status()
            print(f"   db_check() status: {db_result.get('status', 'unknown')}")
            print(f"   server_status() status: {server_result.get('status', 'unknown')}")
            print("   ✅ Aliases work")
        except Exception as e:
            print(f"   ❌ Aliases failed: {e}")
        
        print("\n" + "=" * 60)
        print("NEW MCP FUNCTIONS TEST COMPLETE")
        print("=" * 60)
        print("\n📚 USAGE SUMMARY:")
        print("• get_system_instructions() - Get complete MCP guide")
        print("• help_mcp() - Get help (alias for get_system_instructions)")
        print("• get_operation_help('function_name') - Get specific function help")
        print("• quick_database_check() - Check database connectivity")
        print("• quick_server_status() - Check all server health")
        print("• db_check() - Alias for quick_database_check()")
        print("• server_status() - Alias for quick_server_status()")
        print("\n🎯 These functions provide direct access without complex routing!")
        
    except ImportError as e:
        print(f"❌ Failed to import new MCP functions: {e}")
        print("   Make sure mcp_universal_operations.py has been updated with the new functions")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_new_mcp_functions() 