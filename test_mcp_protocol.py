#!/usr/bin/env python3
"""
Test script to verify MCP server protocol compliance
"""
import json
import subprocess
import sys
import os

def test_mcp_server():
    """Test the MCP server with basic protocol requests"""
    
    # Path to the MCP server
    python_path = r"C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace\BSPclean\Scripts\python.exe"
    script_path = "scripts\\mcp_server_direct.py"
    
    print("Testing MCP Server Protocol...")
    print(f"Python: {python_path}")
    print(f"Script: {script_path}")
    
    try:
        # Start the MCP server process
        process = subprocess.Popen(
            [python_path, script_path, "--mcp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.getcwd()
        )
        
        # Test 1: Initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        print("\n1. Testing initialize request...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"✅ Initialize response: {response}")
        else:
            print("❌ No response to initialize")
            
        # Test 2: List tools request
        list_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        print("\n2. Testing tools/list request...")
        process.stdin.write(json.dumps(list_request) + "\n")
        process.stdin.flush()
        
        # Read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            tools = response.get("result", {}).get("tools", [])
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools[:3]:  # Show first 3 tools
                print(f"   - {tool['name']}: {tool['description']}")
            if len(tools) > 3:
                print(f"   ... and {len(tools) - 3} more")
        else:
            print("❌ No response to tools/list")
            
        # Test 3: Call a simple tool
        call_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_system_instructions",
                "arguments": {}
            }
        }
        
        print("\n3. Testing tool call...")
        process.stdin.write(json.dumps(call_request) + "\n")
        process.stdin.flush()
        
        # Read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print("✅ Tool call successful")
            content = response.get("result", {}).get("content", [])
            if content:
                print(f"   Response length: {len(content[0].get('text', ''))} characters")
        else:
            print("❌ No response to tool call")
            
        # Clean up
        process.terminate()
        process.wait(timeout=5)
        
        print("\n✅ MCP Server Protocol Test Complete")
        
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        if 'process' in locals():
            process.terminate()

if __name__ == "__main__":
    test_mcp_server() 