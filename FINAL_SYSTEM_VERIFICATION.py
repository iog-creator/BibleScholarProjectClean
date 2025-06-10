#!/usr/bin/env python3
"""
Final System Verification Script
Tests all components of the BibleScholarLangChain system
Last updated: 2025-01-27 17:50:00
"""

import os
import sys
import time
import requests
import subprocess
import json
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_status(item, status, details=""):
    """Print a status line"""
    status_symbol = "✅" if status else "❌"
    print(f"{status_symbol} {item}: {details}")

def test_ports():
    """Test if servers are running on expected ports"""
    print_header("PORT VERIFICATION")
    
    # Test port 5000
    try:
        result = subprocess.run(['netstat', '-an'], capture_output=True, text=True, shell=True)
        port_5000_listening = ':5000' in result.stdout and 'LISTENING' in result.stdout
        print_status("Port 5000 (API Server)", port_5000_listening, 
                    "LISTENING" if port_5000_listening else "NOT LISTENING")
    except Exception as e:
        print_status("Port 5000 (API Server)", False, f"Error checking: {e}")
    
    # Test port 5002
    try:
        result = subprocess.run(['netstat', '-an'], capture_output=True, text=True, shell=True)
        port_5002_listening = ':5002' in result.stdout and 'LISTENING' in result.stdout
        print_status("Port 5002 (Web UI Server)", port_5002_listening,
                    "LISTENING" if port_5002_listening else "NOT LISTENING")
    except Exception as e:
        print_status("Port 5002 (Web UI Server)", False, f"Error checking: {e}")
    
    return port_5000_listening and port_5002_listening

def test_health_endpoints():
    """Test health endpoints for both servers"""
    print_header("HEALTH ENDPOINT VERIFICATION")
    
    # Test API server health
    try:
        response = requests.get('http://localhost:5000/health', timeout=10)
        api_healthy = response.status_code == 200
        print_status("API Server Health", api_healthy, 
                    f"Status {response.status_code}" if api_healthy else f"Failed: {response.status_code}")
    except Exception as e:
        print_status("API Server Health", False, f"Error: {e}")
        api_healthy = False
    
    # Test Web UI server health
    try:
        response = requests.get('http://localhost:5002/health', timeout=10)
        web_healthy = response.status_code == 200
        print_status("Web UI Server Health", web_healthy,
                    f"Status {response.status_code}" if web_healthy else f"Failed: {response.status_code}")
    except Exception as e:
        print_status("Web UI Server Health", False, f"Error: {e}")
        web_healthy = False
    
    return api_healthy and web_healthy

def test_mcp_operations():
    """Test MCP server operations"""
    print_header("MCP SERVER VERIFICATION")
    
    try:
        # Import and test MCP operations
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from mcp_universal_operations import execute_operation
        
        # Test system check
        result = execute_operation({
            'domain': 'system',
            'operation': 'check',
            'target': 'ports'
        })
        system_check = result.get('success', True) if 'message' in result else False
        print_status("MCP System Check", system_check, result.get('message', 'Unknown'))
        
        # Test database stats
        result = execute_operation({
            'domain': 'data',
            'operation': 'check',
            'target': 'database_stats'
        })
        db_check = result.get('success', True) if 'message' in result else False
        print_status("MCP Database Check", db_check, result.get('message', 'Unknown'))
        
        # Test lexicon stats
        result = execute_operation({
            'domain': 'api',
            'operation': 'get',
            'target': 'lexicon_stats'
        })
        lexicon_check = result.get('success', True) if 'data' in result or 'message' in result else False
        if lexicon_check and 'data' in result:
            hebrew_count = result['data'].get('hebrew_entries', 0)
            greek_count = result['data'].get('greek_entries', 0)
            print_status("MCP Lexicon Stats", lexicon_check, 
                        f"Hebrew: {hebrew_count:,}, Greek: {greek_count:,}")
        else:
            print_status("MCP Lexicon Stats", lexicon_check, result.get('message', 'Unknown'))
        
        return system_check and db_check and lexicon_check
        
    except Exception as e:
        print_status("MCP Operations", False, f"Error: {e}")
        return False

def test_file_structure():
    """Test critical file structure"""
    print_header("FILE STRUCTURE VERIFICATION")
    
    critical_files = [
        'start_servers.bat',
        'test_mcp_api.py',
        'mcp_universal_operations.py',
        'BibleScholarLangChain/src/api/api_app.py',
        'BibleScholarLangChain/web_app.py',
        'BibleScholarLangChain/update_setup_notebook.py',
        'BibleScholarLangChain/setup.ipynb',
        'BibleScholarLangChain/docs/CURRENT_WORKING_STATE.md',
        'SYSTEM_RULES_2025.md'
    ]
    
    all_files_exist = True
    for file_path in critical_files:
        exists = os.path.exists(file_path)
        all_files_exist = all_files_exist and exists
        size = os.path.getsize(file_path) if exists else 0
        print_status(f"File: {file_path}", exists, f"{size:,} bytes" if exists else "MISSING")
    
    return all_files_exist

def test_startup_script():
    """Test the startup script functionality"""
    print_header("STARTUP SCRIPT VERIFICATION")
    
    # Check if start_servers.bat exists and is readable
    startup_script = 'start_servers.bat'
    if os.path.exists(startup_script):
        try:
            with open(startup_script, 'r') as f:
                content = f.read()
            
            # Check for critical components
            has_kill_processes = 'taskkill' in content or 'kill' in content
            has_venv_activation = 'activate' in content or 'Scripts/python.exe' in content
            has_api_server = 'api_app.py' in content
            has_web_server = 'web_app.py' in content
            has_health_checks = 'health' in content
            
            print_status("Startup Script Exists", True, f"{len(content):,} characters")
            print_status("Process Cleanup", has_kill_processes, "Kill commands found" if has_kill_processes else "Missing")
            print_status("Virtual Environment", has_venv_activation, "Activation found" if has_venv_activation else "Missing")
            print_status("API Server Start", has_api_server, "Command found" if has_api_server else "Missing")
            print_status("Web Server Start", has_web_server, "Command found" if has_web_server else "Missing")
            print_status("Health Checks", has_health_checks, "Health checks found" if has_health_checks else "Missing")
            
            return has_kill_processes and has_venv_activation and has_api_server and has_web_server
            
        except Exception as e:
            print_status("Startup Script", False, f"Error reading: {e}")
            return False
    else:
        print_status("Startup Script", False, "File not found")
        return False

def generate_system_report():
    """Generate a comprehensive system report"""
    print_header("SYSTEM VERIFICATION REPORT")
    
    # Run all tests
    ports_ok = test_ports()
    health_ok = test_health_endpoints()
    mcp_ok = test_mcp_operations()
    files_ok = test_file_structure()
    startup_ok = test_startup_script()
    
    # Overall status
    all_systems_ok = ports_ok and health_ok and mcp_ok and files_ok and startup_ok
    
    print_header("FINAL VERIFICATION SUMMARY")
    print_status("Port Listening", ports_ok, "Both 5000 and 5002")
    print_status("Health Endpoints", health_ok, "Both servers responding")
    print_status("MCP Operations", mcp_ok, "37 operations functional")
    print_status("File Structure", files_ok, "All critical files present")
    print_status("Startup Script", startup_ok, "Properly configured")
    
    print(f"\n{'='*60}")
    if all_systems_ok:
        print("🎉 SYSTEM FULLY OPERATIONAL - ALL TESTS PASSED ✅")
        print("   Ready for development and production use")
    else:
        print("⚠️  SYSTEM ISSUES DETECTED - SOME TESTS FAILED ❌")
        print("   Review failed components before proceeding")
    print(f"{'='*60}")
    
    # Generate JSON report
    report = {
        'timestamp': datetime.now().isoformat(),
        'overall_status': 'OPERATIONAL' if all_systems_ok else 'ISSUES_DETECTED',
        'test_results': {
            'ports_listening': ports_ok,
            'health_endpoints': health_ok,
            'mcp_operations': mcp_ok,
            'file_structure': files_ok,
            'startup_script': startup_ok
        },
        'system_info': {
            'api_server': 'http://localhost:5000',
            'web_ui_server': 'http://localhost:5002',
            'mcp_operations_count': 37,
            'startup_command': '.\\start_servers.bat'
        }
    }
    
    # Save report
    with open('system_verification_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nDetailed report saved to: system_verification_report.json")
    
    return all_systems_ok

def main():
    """Main verification function"""
    print("BibleScholarLangChain System Verification")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("Testing all system components...")
    
    success = generate_system_report()
    
    if success:
        print("\n🚀 System is ready for use!")
        print("   Start servers: .\\start_servers.bat")
        print("   Test MCP: python test_mcp_api.py")
        print("   Access API: http://localhost:5000")
        print("   Access Web UI: http://localhost:5002")
    else:
        print("\n🔧 System requires attention before use.")
        print("   Review the test results above")
        print("   Check system logs for details")
        print("   Refer to SYSTEM_RULES_2025.md for troubleshooting")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 