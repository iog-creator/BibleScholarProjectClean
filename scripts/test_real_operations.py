#!/usr/bin/env python3
"""
Test script for real database operations
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from mcp_universal_operations import execute_operation

def test_real_operations():
    """Test the real database operations"""
    print("🧪 Testing Real Database Operations")
    print("=" * 50)
    
    # Test 1: Real Hebrew word analysis
    print("\n1. Testing Hebrew Word Analysis...")
    result = execute_operation({
        "domain": "data",
        "operation": "analyze", 
        "target": "hebrew_words",
        "action_params": {"search_term": "love", "limit": 3},
        "validation_level": "comprehensive"
    })
    
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    if 'hebrew_words' in result.get('results', {}):
        print("✅ REAL database query executed!")
        print(f"Found {len(result['results']['hebrew_words'])} Hebrew words")
    else:
        print("❌ Still using placeholder")
    
    # Test 2: Real database stats
    print("\n2. Testing Database Stats...")
    result = execute_operation({
        "domain": "data",
        "operation": "check",
        "target": "database_stats", 
        "validation_level": "comprehensive"
    })
    
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    if 'langchain_collections' in result.get('results', {}).get('totals', {}):
        print("✅ REAL database stats retrieved!")
        totals = result['results']['totals']
        print(f"LangChain collections: {totals.get('langchain_collections', 'N/A')}")
        print(f"LangChain embeddings: {totals.get('langchain_embeddings', 'N/A')}")
        print(f"Database type: {totals.get('database_type', 'N/A')}")
    elif 'table_count' in result.get('results', {}):
        print("❌ Still using placeholder")
        print(f"Placeholder result: {result['results']}")
    else:
        print("❓ Unexpected result format")
        print(f"Results: {result.get('results', {})}")
    
    # Test 3: Real Hebrew analysis
    print("\n3. Testing Hebrew Analysis (LangChain adapted)...")
    result = execute_operation({
        "domain": "data",
        "operation": "analyze",
        "target": "hebrew_words",
        "action_params": {"search_term": "love", "limit": 3},
        "validation_level": "comprehensive"
    })
    
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    if 'langchain_results' in result.get('results', {}):
        print("✅ REAL Hebrew analysis (LangChain adapted)!")
        print(f"Total embeddings: {result['results'].get('total_embeddings', 'N/A')}")
        print(f"Results found: {result['results'].get('results_count', 'N/A')}")
    elif 'word_count' in result.get('results', {}):
        print("❌ Still using placeholder")
        print(f"Placeholder result: {result['results']}")
    else:
        print("❓ Unexpected result format")
        print(f"Results: {result.get('results', {})}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Complete!")

if __name__ == "__main__":
    test_real_operations() 