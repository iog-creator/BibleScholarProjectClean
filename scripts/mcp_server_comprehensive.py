#!/usr/bin/env python3
"""
Comprehensive MCP Server for Bible Scholar Project
"""
import json
import sys
import logging
import os
from datetime import datetime

# Set up logging
log_file = os.path.join(os.getcwd(), 'mcp_comprehensive.log')
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

class MCPServer:
    def __init__(self):
        self.tools = [
            {
                "name": "hello_world",
                "description": "Simple hello world test",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name to greet"
                        }
                    },
                    "additionalProperties": False
                }
            },
            {
                "name": "get_system_info",
                "description": "Get system information",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "quick_database_check",
                "description": "Check database connectivity and basic stats",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "list_available_operations",
                "description": "List all available Bible Scholar operations",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            }
        ]
    
    def handle_initialize(self, request_id):
        """Handle initialize request"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "bible-scholar-comprehensive",
                    "version": "1.0.0"
                }
            }
        }
    
    def handle_tools_list(self, request_id):
        """Handle tools/list request"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": self.tools
            }
        }
    
    def handle_tools_call(self, request_id, params):
        """Handle tools/call request"""
        tool_name = params.get('name')
        arguments = params.get('arguments', {})
        
        logger.info(f"Calling tool: {tool_name} with args: {arguments}")
        
        if tool_name == "hello_world":
            name = arguments.get('name', 'World')
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Hello, {name}! MCP Server is working perfectly."
                        }
                    ]
                }
            }
        
        elif tool_name == "get_system_info":
            info = {
                "timestamp": datetime.now().isoformat(),
                "python_version": sys.version,
                "working_directory": os.getcwd(),
                "environment_vars": {
                    "PYTHONPATH": os.environ.get("PYTHONPATH", "Not set"),
                    "MCP_DEBUG": os.environ.get("MCP_DEBUG", "Not set")
                }
            }
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"System Information:\n{json.dumps(info, indent=2)}"
                        }
                    ]
                }
            }
        
        elif tool_name == "quick_database_check":
            try:
                # Try to import and use the database check
                sys.path.append(os.getcwd())
                from mcp_universal_operations import quick_database_check
                result = quick_database_check()
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Database Check Result:\n{json.dumps(result, indent=2)}"
                            }
                        ]
                    }
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Database check failed: {str(e)}"
                            }
                        ]
                    }
                }
        
        elif tool_name == "list_available_operations":
            try:
                # Try to import and list operations
                sys.path.append(os.getcwd())
                from mcp_universal_operations import get_system_instructions
                result = get_system_instructions()
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Available Operations:\n{result}"
                            }
                        ]
                    }
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Could not list operations: {str(e)}"
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
                    "message": f"Tool {tool_name} not found"
                }
            }
    
    def handle_request(self, request):
        """Handle MCP requests"""
        method = request.get('method')
        request_id = request.get('id')
        params = request.get('params', {})
        
        logger.info(f"Handling request: {method}")
        
        if method == 'initialize':
            return self.handle_initialize(request_id)
        elif method == 'tools/list':
            return self.handle_tools_list(request_id)
        elif method == 'tools/call':
            return self.handle_tools_call(request_id, params)
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
    logger.info("Starting comprehensive MCP server...")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Python path: {sys.path}")
    
    server = MCPServer()
    
    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                logger.info("No input, exiting...")
                break
            
            try:
                request = json.loads(line.strip())
                logger.debug(f"Request: {request}")
                
                response = server.handle_request(request)
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