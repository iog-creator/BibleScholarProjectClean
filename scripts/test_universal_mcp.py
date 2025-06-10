#!/usr/bin/env python3
"""
Test Script for Universal MCP Architecture
Validates the refactored MCP server functionality
"""
import sys
import time
import json
from typing import Dict, Any, List
from mcp_server_refactored import mcp_server, migrate_old_function_call, get_performance_comparison

def test_universal_operations():
    """Test all universal operation categories"""
    print("🧪 Testing Universal MCP Operations")
    print("=" * 50)
    
    test_results = {}
    
    # Test 1: Rules Domain Operations
    print("\n📋 Testing Rules Domain...")
    rules_tests = [
        {
            "name": "Database Rules",
            "params": {"domain": "rules", "operation": "enforce", "target": "database"}
        },
        {
            "name": "Hebrew Rules", 
            "params": {"domain": "rules", "operation": "enforce", "target": "hebrew"}
        },
        {
            "name": "All Rules",
            "params": {"domain": "batch", "operation": "enforce", "target": "all_rules"}
        }
    ]
    
    for test in rules_tests:
        result = mcp_server.handle_function_call("execute_operation", test["params"])
        test_results[test["name"]] = result
        status = "✅" if result["status"] == "success" else "❌"
        print(f"  {status} {test['name']}: {result['message']}")
    
    # Test 2: System Domain Operations
    print("\n🖥️ Testing System Domain...")
    system_tests = [
        {
            "name": "Port Check",
            "params": {
                "domain": "system", 
                "operation": "check", 
                "target": "ports",
                "action_params": {"ports": [5000, 5432]}
            }
        },
        {
            "name": "Data Verification",
            "params": {"domain": "system", "operation": "verify", "target": "data"}
        },
        {
            "name": "Database Query",
            "params": {
                "domain": "system", 
                "operation": "query", 
                "target": "database",
                "action_params": {"query": "SELECT 1 as test", "description": "Test query"}
            }
        }
    ]
    
    for test in system_tests:
        result = mcp_server.handle_function_call("execute_operation", test["params"])
        test_results[test["name"]] = result
        status = "✅" if result["status"] == "success" else "❌"
        print(f"  {status} {test['name']}: {result['message']}")
    
    # Test 3: Integration Domain Operations
    print("\n🔗 Testing Integration Domain...")
    integration_tests = [
        {
            "name": "V2 API Copy",
            "params": {
                "domain": "integration",
                "operation": "copy", 
                "target": "v2_api",
                "action_params": {"api_name": "dspy_api"}
            }
        }
    ]
    
    for test in integration_tests:
        result = mcp_server.handle_function_call("execute_operation", test["params"])
        test_results[test["name"]] = result
        status = "✅" if result["status"] == "success" else "❌"
        print(f"  {status} {test['name']}: {result['message']}")
    
    # Test 4: Utility Domain Operations
    print("\n🛠️ Testing Utility Domain...")
    utility_tests = [
        {
            "name": "Action Logging",
            "params": {
                "domain": "utility",
                "operation": "log",
                "target": "action", 
                "action_params": {
                    "action": "Universal MCP architecture tested",
                    "details": "All operation domains validated successfully"
                }
            }
        }
    ]
    
    for test in utility_tests:
        result = mcp_server.handle_function_call("execute_operation", test["params"])
        test_results[test["name"]] = result
        status = "✅" if result["status"] == "success" else "❌"
        print(f"  {status} {test['name']}: {result['message']}")
    
    return test_results

def test_migration_compatibility():
    """Test backward compatibility with old function calls"""
    print("\n🔄 Testing Migration Compatibility")
    print("=" * 50)
    
    migration_results = {}
    
    # Test old function calls
    old_functions = [
        "mcp_bible-scholar-mcp_check_ports",
        "mcp_bible-scholar-mcp_enforce_database_rules", 
        "mcp_bible-scholar-mcp_log_action",
        "mcp_bible-scholar-mcp_enforce_all_rules"
    ]
    
    for old_func in old_functions:
        result = migrate_old_function_call(old_func, {"test": "migration"})
        migration_results[old_func] = result
        status = "✅" if result["status"] == "success" else "❌"
        print(f"  {status} {old_func}: {result['message']}")
    
    return migration_results

def test_performance_metrics():
    """Test and display performance metrics"""
    print("\n📊 Performance Metrics")
    print("=" * 50)
    
    # Test execution time
    start_time = time.time()
    
    # Execute multiple operations
    operations = [
        {"domain": "rules", "operation": "enforce", "target": "database"},
        {"domain": "system", "operation": "check", "target": "ports"},
        {"domain": "utility", "operation": "log", "target": "action"},
        {"domain": "batch", "operation": "enforce", "target": "all_rules"}
    ]
    
    for op in operations:
        mcp_server.handle_function_call("execute_operation", op)
    
    execution_time = time.time() - start_time
    
    # Get performance comparison
    perf_comparison = get_performance_comparison()
    
    print(f"  ⚡ Batch execution time: {execution_time:.3f}s")
    print(f"  📈 Function efficiency: {perf_comparison['architecture_comparison']['improvement_metrics']['function_efficiency']}")
    print(f"  🎯 Slot utilization: {perf_comparison['architecture_comparison']['improvement_metrics']['slot_utilization']}")
    print(f"  🚀 Operation capacity: {perf_comparison['architecture_comparison']['improvement_metrics']['operation_capacity']}")
    
    return {
        "execution_time": execution_time,
        "performance_comparison": perf_comparison
    }

def test_error_handling():
    """Test error handling and validation"""
    print("\n🚨 Testing Error Handling")
    print("=" * 50)
    
    error_tests = [
        {
            "name": "Missing Domain",
            "params": {"operation": "test", "target": "something"}
        },
        {
            "name": "Invalid Domain",
            "params": {"domain": "invalid", "operation": "test", "target": "something"}
        },
        {
            "name": "Unknown Function",
            "function": "unknown_function",
            "params": {}
        }
    ]
    
    error_results = {}
    
    for test in error_tests:
        if test["name"] == "Unknown Function":
            result = mcp_server.handle_function_call(test["function"], test["params"])
        else:
            result = mcp_server.handle_function_call("execute_operation", test["params"])
        
        error_results[test["name"]] = result
        status = "✅" if result["status"] == "error" else "❌"  # We expect errors here
        print(f"  {status} {test['name']}: {result['message']}")
    
    return error_results

def test_dynamic_operations():
    """Test dynamic operation handling"""
    print("\n🎯 Testing Dynamic Operations")
    print("=" * 50)
    
    dynamic_tests = [
        {
            "name": "Custom Rule Enforcement",
            "params": {"domain": "rules", "operation": "enforce", "target": "custom_rule"}
        },
        {
            "name": "Custom System Check", 
            "params": {"domain": "system", "operation": "check", "target": "custom_component"}
        },
        {
            "name": "Custom Integration",
            "params": {"domain": "integration", "operation": "deploy", "target": "custom_service"}
        }
    ]
    
    dynamic_results = {}
    
    for test in dynamic_tests:
        result = mcp_server.handle_function_call("execute_operation", test["params"])
        dynamic_results[test["name"]] = result
        status = "✅" if result["status"] == "success" else "❌"
        print(f"  {status} {test['name']}: {result['message']}")
    
    return dynamic_results

def generate_test_report(all_results: Dict[str, Any]):
    """Generate comprehensive test report"""
    print("\n📋 COMPREHENSIVE TEST REPORT")
    print("=" * 60)
    
    total_tests = 0
    passed_tests = 0
    
    for category, results in all_results.items():
        if isinstance(results, dict) and "status" not in results:  # It's a category of tests
            category_total = len(results)
            category_passed = sum(1 for r in results.values() if r.get("status") == "success")
            
            total_tests += category_total
            passed_tests += category_passed
            
            print(f"\n{category}:")
            print(f"  Tests: {category_passed}/{category_total}")
            print(f"  Success Rate: {(category_passed/category_total)*100:.1f}%")
    
    overall_success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"\n🎯 OVERALL RESULTS:")
    print(f"  Total Tests: {total_tests}")
    print(f"  Passed: {passed_tests}")
    print(f"  Success Rate: {overall_success_rate:.1f}%")
    
    if overall_success_rate >= 90:
        print("  Status: ✅ EXCELLENT - Universal architecture working perfectly!")
    elif overall_success_rate >= 75:
        print("  Status: ✅ GOOD - Minor issues to address")
    else:
        print("  Status: ❌ NEEDS WORK - Significant issues found")
    
    return {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "success_rate": overall_success_rate
    }

def main():
    """Main test execution"""
    print("🚀 UNIVERSAL MCP ARCHITECTURE TEST SUITE")
    print("=" * 60)
    
    # Get server info
    server_info = mcp_server.get_server_info()
    print(f"Testing: {server_info['server_name']} v{server_info['version']}")
    print(f"Architecture: {server_info['architecture']}")
    print(f"Function Slots Used: {server_info['function_slots_used']}")
    print(f"Available Slots: {server_info['function_slots_available']}")
    
    # Run all tests
    all_results = {}
    
    try:
        all_results["Universal Operations"] = test_universal_operations()
        all_results["Migration Compatibility"] = test_migration_compatibility()
        all_results["Performance Metrics"] = test_performance_metrics()
        all_results["Error Handling"] = test_error_handling()
        all_results["Dynamic Operations"] = test_dynamic_operations()
        
        # Generate final report
        final_report = generate_test_report(all_results)
        
        # Save results to file
        with open("universal_mcp_test_results.json", "w") as f:
            json.dump({
                "server_info": server_info,
                "test_results": all_results,
                "final_report": final_report,
                "timestamp": time.time()
            }, f, indent=2)
        
        print(f"\n💾 Test results saved to: universal_mcp_test_results.json")
        
        return final_report["success_rate"] >= 90
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 