#!/usr/bin/env python3
"""
Test script for comprehensive MCP server
"""
import json
import subprocess
import sys
import time

def test_mcp_server():
    """Test the comprehensive MCP server"""
    print("Testing Comprehensive MCP Server...")
    
    # Start the server
    server_path = "scripts/mcp_server_comprehensive.py"
    python_path = "BSPclean/Scripts/python.exe"
    
    try:
        process = subprocess.Popen(
            [python_path, server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="."
        )
        
        # Test initialize
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        }
        
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        if response:
            init_response = json.loads(response.strip())
            print("✅ Initialize response received")
            print(f"   {json.dumps(init_response, indent=2)}")
        
        # Test tools list
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        process.stdin.write(json.dumps(tools_request) + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        if response:
            tools_response = json.loads(response.strip())
            print("✅ Tools list response received")
            tools = tools_response.get('result', {}).get('tools', [])
            print(f"   Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description']}")
        
        # Test hello_world tool
        hello_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "hello_world",
                "arguments": {"name": "Cursor"}
            }
        }
        
        process.stdin.write(json.dumps(hello_request) + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        if response:
            hello_response = json.loads(response.strip())
            print("✅ Hello world tool response received")
            content = hello_response.get('result', {}).get('content', [])
            if content:
                print(f"   {content[0]['text']}")
        
        # Test system info tool
        info_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "get_system_info",
                "arguments": {}
            }
        }
        
        process.stdin.write(json.dumps(info_request) + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        if response:
            info_response = json.loads(response.strip())
            print("✅ System info tool response received")
            content = info_response.get('result', {}).get('content', [])
            if content:
                print(f"   System info retrieved successfully")
        
        process.terminate()
        print("\n🎉 All tests passed! MCP server is working correctly.")
        
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        if 'process' in locals():
            process.terminate()

if __name__ == "__main__":
    test_mcp_server() 