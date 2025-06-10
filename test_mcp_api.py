#!/usr/bin/env python3
"""
Test script for MCP API functionality
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_universal_operations import execute_operation

def test_mcp_api():
    """Test MCP API operations"""
    print("=== TESTING MCP API OPERATIONS ===")
    
    # Test 1: System port check
    print("\n1. Testing system port check...")
    try:
        result = execute_operation({
            'domain': 'system', 
            'operation': 'check', 
            'target': 'ports'
        })
        print(f"✅ Port check: {result.get('message', 'Unknown')}")
    except Exception as e:
        print(f"❌ Port check failed: {e}")
    
    # Test 2: Database stats
    print("\n2. Testing database stats...")
    try:
        result = execute_operation({
            'domain': 'data', 
            'operation': 'check', 
            'target': 'database_stats'
        })
        print(f"✅ Database stats: {result.get('message', 'Unknown')}")
    except Exception as e:
        print(f"❌ Database stats failed: {e}")
    
    # Test 3: Lexicon stats (new API operation)
    print("\n3. Testing lexicon stats API...")
    try:
        result = execute_operation({
            'domain': 'api', 
            'operation': 'get', 
            'target': 'lexicon_stats'
        })
        print(f"✅ Lexicon stats: {result.get('message', 'Unknown')}")
        if result.get('status') == 'success' and 'results' in result:
            stats = result['results']
            print(f"   Hebrew entries: {stats.get('hebrew_entries', 'N/A')}")
            print(f"   Greek entries: {stats.get('greek_entries', 'N/A')}")
    except Exception as e:
        print(f"❌ Lexicon stats failed: {e}")
    
    print("\n=== MCP API TEST COMPLETE ===")

if __name__ == "__main__":
    test_mcp_api() 