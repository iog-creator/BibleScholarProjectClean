#!/usr/bin/env python3
"""
Test the minimal MCP server
"""
import json
import subprocess
import sys

def test_minimal_server():
    """Test the minimal MCP server"""
    
    python_path = r"C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace\BSPclean\Scripts\python.exe"
    script_path = "scripts\\mcp_server_minimal.py"
    
    print("Testing Minimal MCP Server...")
    
    try:
        process = subprocess.Popen(
            [python_path, script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
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
            print("✅ Initialize response received")
            print(f"   {response.strip()}")
        else:
            print("❌ No initialize response")
            
        # Test tools list
        list_request = {
            "jsonrpc": "2.0", 
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        process.stdin.write(json.dumps(list_request) + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        if response:
            print("✅ Tools list response received")
            data = json.loads(response.strip())
            tools = data.get("result", {}).get("tools", [])
            print(f"   Found {len(tools)} tools")
        else:
            print("❌ No tools list response")
            
        process.terminate()
        process.wait(timeout=5)
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_minimal_server() 