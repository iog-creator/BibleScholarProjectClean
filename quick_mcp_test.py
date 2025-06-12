#!/usr/bin/env python3
"""
Quick test to verify MCP server tools
"""
import json
import subprocess
import sys

def test_tools():
    """Test what tools are available"""
    print("Testing MCP Server Tools...")
    
    python_path = "BSPclean/Scripts/python.exe"
    server_path = "scripts/mcp_server_comprehensive.py"
    
    try:
        # Start server
        process = subprocess.Popen(
            [python_path, server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Initialize
        init_msg = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
        process.stdin.write(json.dumps(init_msg) + "\n")
        process.stdin.flush()
        
        # Read response
        response = process.stdout.readline()
        print(f"Initialize: {response.strip()}")
        
        # Get tools list
        tools_msg = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        process.stdin.write(json.dumps(tools_msg) + "\n")
        process.stdin.flush()
        
        # Read tools response
        tools_response = process.stdout.readline()
        print(f"Tools response: {tools_response.strip()}")
        
        # Parse and display tools
        try:
            tools_data = json.loads(tools_response.strip())
            tools = tools_data.get('result', {}).get('tools', [])
            print(f"\n🔧 Found {len(tools)} tools:")
            for i, tool in enumerate(tools, 1):
                print(f"  {i}. {tool['name']} - {tool['description']}")
        except:
            print("Could not parse tools response")
        
        process.terminate()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_tools() 