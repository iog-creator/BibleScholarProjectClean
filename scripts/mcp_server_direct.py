#!/usr/bin/env python3
"""
Direct MCP Server for Bible Scholar Project
Exposes all quick functions as individual MCP tools for easier access
"""
import json
import logging
import sys
import os
from typing import Dict, Any, List

# Import from workspace root
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from mcp_universal_operations import (
    quick_database_check, quick_server_status, quick_hebrew_analysis,
    quick_greek_analysis, quick_verse_search, quick_lexicon_search,
    quick_vector_search, quick_start_servers, quick_stop_servers,
    quick_rule_check, get_system_instructions, get_operation_help,
    execute_operation
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BibleScholarDirectMCPServer:
    """
    Direct MCP Server that exposes all quick functions as individual tools
    """
    
    def __init__(self):
        self.server_name = "BibleScholar-Direct-MCP"
        self.version = "1.0.0"
        
    def get_available_tools(self) -> List[Dict]:
        """Define all available MCP tools"""
        return [
            {
                "name": "quick_database_check",
                "description": "Quick database connectivity check and basic stats",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "quick_server_status", 
                "description": "Check status of API, Web UI, and LM Studio servers",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "quick_hebrew_analysis",
                "description": "Analyze Hebrew words with morphology data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "word": {
                            "type": "string",
                            "description": "Hebrew word to analyze"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 10
                        }
                    },
                    "required": ["word"]
                }
            },
            {
                "name": "quick_greek_analysis",
                "description": "Analyze Greek words with morphology data", 
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "word": {
                            "type": "string",
                            "description": "Greek word to analyze"
                        },
                        "limit": {
                            "type": "integer", 
                            "description": "Maximum number of results",
                            "default": 10
                        }
                    },
                    "required": ["word"]
                }
            },
            {
                "name": "quick_verse_search",
                "description": "Search verses across Bible translations",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for verses"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results", 
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "quick_lexicon_search",
                "description": "Search Hebrew or Greek lexicon entries",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "term": {
                            "type": "string",
                            "description": "Term to search for"
                        },
                        "language": {
                            "type": "string",
                            "enum": ["hebrew", "greek"],
                            "description": "Language to search in"
                        }
                    },
                    "required": ["term", "language"]
                }
            },
            {
                "name": "quick_vector_search",
                "description": "Semantic similarity search using vector embeddings",
                "inputSchema": {
                    "type": "object", 
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Query for semantic search"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "quick_start_servers",
                "description": "Start all Bible Scholar servers (API, Web UI, LM Studio)",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "quick_stop_servers",
                "description": "Stop all Bible Scholar servers",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "quick_rule_check",
                "description": "Check compliance with project rules",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "rule_type": {
                            "type": "string",
                            "description": "Type of rule to check (e.g., 'etl', 'database', 'hebrew')"
                        }
                    },
                    "required": ["rule_type"]
                }
            },
            {
                "name": "get_system_instructions",
                "description": "Get comprehensive system usage instructions",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "get_operation_help",
                "description": "Get detailed help for specific operations",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "operation_name": {
                            "type": "string",
                            "description": "Name of operation to get help for"
                        }
                    },
                    "required": ["operation_name"]
                }
            },
            {
                "name": "execute_operation",
                "description": "Universal operation executor (for complex operations)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "params": {
                            "type": "object",
                            "description": "Parameters for the operation"
                        }
                    }
                }
            }
        ]
    
    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP tool calls"""
        try:
            if tool_name == "quick_database_check":
                return quick_database_check()
            elif tool_name == "quick_server_status":
                return quick_server_status()
            elif tool_name == "quick_hebrew_analysis":
                word = arguments.get("word")
                limit = arguments.get("limit", 10)
                return quick_hebrew_analysis(word, limit)
            elif tool_name == "quick_greek_analysis":
                word = arguments.get("word")
                limit = arguments.get("limit", 10)
                return quick_greek_analysis(word, limit)
            elif tool_name == "quick_verse_search":
                query = arguments.get("query")
                limit = arguments.get("limit", 10)
                return quick_verse_search(query, limit)
            elif tool_name == "quick_lexicon_search":
                term = arguments.get("term")
                language = arguments.get("language")
                return quick_lexicon_search(term, language)
            elif tool_name == "quick_vector_search":
                query = arguments.get("query")
                limit = arguments.get("limit", 10)
                return quick_vector_search(query, limit)
            elif tool_name == "quick_start_servers":
                return quick_start_servers()
            elif tool_name == "quick_stop_servers":
                return quick_stop_servers()
            elif tool_name == "quick_rule_check":
                rule_type = arguments.get("rule_type")
                return quick_rule_check(rule_type)
            elif tool_name == "get_system_instructions":
                return get_system_instructions()
            elif tool_name == "get_operation_help":
                operation_name = arguments.get("operation_name")
                return get_operation_help(operation_name)
            elif tool_name == "execute_operation":
                params = arguments.get("params", {})
                return execute_operation(params)
            else:
                return {
                    "status": "error",
                    "message": f"Unknown tool: {tool_name}",
                    "available_tools": [tool["name"] for tool in self.get_available_tools()]
                }
        except Exception as e:
            logger.error(f"Error executing {tool_name}: {str(e)}")
            return {
                "status": "error",
                "message": f"Error executing {tool_name}: {str(e)}"
            }

# Global server instance
mcp_server = BibleScholarDirectMCPServer()

# ========== MCP PROTOCOL HANDLING ==========

def handle_mcp_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP protocol requests"""
    method = request.get('method')
    request_id = request.get('id')
    params = request.get('params', {})
    
    try:
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
                        "name": "bible-scholar-direct-mcp",
                        "version": "1.0.0"
                    }
                }
            }
        
        elif method == 'tools/list':
            tools = mcp_server.get_available_tools()
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": tools}
            }
        
        elif method == 'tools/call':
            tool_name = params.get('name')
            tool_arguments = params.get('arguments', {})
            
            result = mcp_server.handle_tool_call(tool_name, tool_arguments)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
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
    
    except Exception as e:
        logger.error(f"Error handling MCP request: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }

def run_mcp_server():
    """Run the MCP server"""
    logger.info("Starting Bible Scholar Direct MCP Server...")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    
    try:
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    logger.info("No more input, exiting...")
                    break
                
                logger.debug(f"Received request: {line.strip()}")
                request = json.loads(line.strip())
                response = handle_mcp_request(request)
                
                response_json = json.dumps(response)
                logger.debug(f"Sending response: {response_json}")
                print(response_json)
                sys.stdout.flush()
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
                continue
            except Exception as e:
                logger.error(f"Error processing request: {e}")
                error_response = {
                    "jsonrpc": "2.0", 
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
                continue
                
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")

if __name__ == "__main__":
    if "--mcp" in sys.argv:
        # Set up more detailed logging for MCP mode
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('mcp_server.log'),
                logging.StreamHandler(sys.stderr)
            ]
        )
        run_mcp_server()
    else:
        print("Bible Scholar Direct MCP Server")
        print("Available tools:")
        for tool in mcp_server.get_available_tools():
            print(f"  - {tool['name']}: {tool['description']}") 