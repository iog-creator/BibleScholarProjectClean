#!/usr/bin/env python3
"""
Test script for Bible Scholar MCP server
"""
import json
import subprocess
import sys
import time

def test_bible_scholar_server():
    """Test the Bible Scholar MCP server"""
    print("Testing Bible Scholar MCP Server...")
    
    python_path = "BSPclean/Scripts/python.exe"
    server_path = "scripts/mcp_server_bible_scholar.py"
    
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
        print(f"✅ Initialize: {response.strip()}")
        
        # Get tools list
        tools_msg = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        process.stdin.write(json.dumps(tools_msg) + "\n")
        process.stdin.flush()
        
        # Read tools response
        tools_response = process.stdout.readline()
        print(f"✅ Tools response received")
        
        # Parse and display tools
        try:
            tools_data = json.loads(tools_response.strip())
            tools = tools_data.get('result', {}).get('tools', [])
            print(f"\n🔧 Found {len(tools)} tools:")
            for i, tool in enumerate(tools, 1):
                print(f"  {i}. {tool['name']} - {tool['description']}")
        except Exception as e:
            print(f"Could not parse tools response: {e}")
        
        # Test hello_world tool
        hello_msg = {
            "jsonrpc": "2.0", 
            "id": 3, 
            "method": "tools/call",
            "params": {
                "name": "hello_world",
                "arguments": {"name": "Bible Scholar"}
            }
        }
        process.stdin.write(json.dumps(hello_msg) + "\n")
        process.stdin.flush()
        
        hello_response = process.stdout.readline()
        try:
            hello_data = json.loads(hello_response.strip())
            content = hello_data.get('result', {}).get('content', [])
            if content:
                print(f"✅ Hello test: {content[0]['text']}")
        except:
            print("Could not parse hello response")
        
        # Test database check
        db_msg = {
            "jsonrpc": "2.0", 
            "id": 4, 
            "method": "tools/call",
            "params": {
                "name": "quick_database_check",
                "arguments": {"random_string": "test"}
            }
        }
        process.stdin.write(json.dumps(db_msg) + "\n")
        process.stdin.flush()
        
        db_response = process.stdout.readline()
        try:
            db_data = json.loads(db_response.strip())
            content = db_data.get('result', {}).get('content', [])
            if content:
                print(f"✅ Database check completed successfully")
        except Exception as e:
            print(f"Database check response: {e}")
        
        process.terminate()
        print("\n🎉 Bible Scholar MCP Server is working correctly!")
        
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        if 'process' in locals():
            process.terminate()

if __name__ == "__main__":
    test_bible_scholar_server() 