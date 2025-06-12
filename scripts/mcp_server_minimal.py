#!/usr/bin/env python3
"""
Minimal MCP Server for testing connectivity with Cursor
"""
import json
import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_minimal.log'),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

def handle_request(request):
    """Handle MCP requests"""
    method = request.get('method')
    request_id = request.get('id')
    
    logger.info(f"Handling request: {method}")
    
    if method == 'initialize':
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "bible-scholar-minimal",
                    "version": "1.0.0"
                }
            }
        }
    
    elif method == 'tools/list':
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [
                    {
                        "name": "test_tool",
                        "description": "A simple test tool",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                            "additionalProperties": False
                        }
                    }
                ]
            }
        }
    
    elif method == 'tools/call':
        tool_name = request.get('params', {}).get('name')
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": f"Hello from {tool_name}! MCP server is working."
                    }
                ]
            }
        }
    
    else:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": f"Method {method} not found"
            }
        }

def main():
    """Main server loop"""
    logger.info("Starting minimal MCP server...")
    
    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                logger.info("No input, exiting...")
                break
            
            try:
                request = json.loads(line.strip())
                logger.debug(f"Request: {request}")
                
                response = handle_request(request)
                logger.debug(f"Response: {response}")
                
                print(json.dumps(response))
                sys.stdout.flush()
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
            except Exception as e:
                logger.error(f"Error: {e}")
                
    except KeyboardInterrupt:
        logger.info("Server stopped")

if __name__ == "__main__":
    main() 