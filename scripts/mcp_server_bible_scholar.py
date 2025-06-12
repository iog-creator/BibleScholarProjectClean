#!/usr/bin/env python3
"""
Bible Scholar MCP Server - Exposes Bible Scholar functionality as MCP tools
"""
import json
import sys
import logging
import os
from datetime import datetime
import platform

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the existing functionality
from mcp_universal_operations import (
    quick_database_check, quick_server_status, quick_hebrew_analysis,
    quick_greek_analysis, quick_verse_search, quick_lexicon_search,
    quick_vector_search, quick_start_servers, quick_stop_servers,
    quick_rule_check, get_system_instructions, get_operation_help
)

# Set up logging
log_file = os.path.join(os.path.dirname(__file__), '..', 'mcp_bible_scholar.log')
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

class BibleScholarMCPServer:
    def __init__(self):
        self.tools = [
            {
                "name": "quick_database_check",
                "description": "Check database connectivity and basic stats for Hebrew/Greek lexicons",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "quick_server_status", 
                "description": "Check status of all Bible Scholar servers (API, Web UI, LM Studio)",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "quick_hebrew_analysis",
                "description": "Analyze Hebrew words with morphology and lexicon data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "word": {
                            "type": "string",
                            "description": "Hebrew word to analyze (optional)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 10
                        }
                    },
                    "additionalProperties": False
                }
            },
            {
                "name": "quick_greek_analysis",
                "description": "Analyze Greek words with morphology and lexicon data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "word": {
                            "type": "string", 
                            "description": "Greek word to analyze (optional)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 10
                        }
                    },
                    "additionalProperties": False
                }
            },
            {
                "name": "quick_verse_search",
                "description": "Search Bible verses across multiple translations",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for Bible verses"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 5
                        }
                    },
                    "required": ["query"],
                    "additionalProperties": False
                }
            },
            {
                "name": "quick_lexicon_search",
                "description": "Search Hebrew/Greek lexicon for terms and definitions",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "term": {
                            "type": "string",
                            "description": "Term to search in lexicon"
                        },
                        "language": {
                            "type": "string",
                            "description": "Language to search (hebrew, greek, or both)",
                            "default": "both"
                        }
                    },
                    "required": ["term"],
                    "additionalProperties": False
                }
            },
            {
                "name": "quick_vector_search",
                "description": "Perform semantic similarity search using vector embeddings",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Query for semantic search"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 5
                        }
                    },
                    "required": ["query"],
                    "additionalProperties": False
                }
            },
            {
                "name": "quick_start_servers",
                "description": "Start Bible Scholar API and Web UI servers",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "quick_stop_servers",
                "description": "Stop Bible Scholar API and Web UI servers", 
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "quick_rule_check",
                "description": "Check compliance with Bible Scholar project rules",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "rule_type": {
                            "type": "string",
                            "description": "Type of rules to check (all, database, etl, hebrew, etc.)",
                            "default": "all"
                        }
                    },
                    "additionalProperties": False
                }
            },
            {
                "name": "get_system_instructions",
                "description": "Get comprehensive Bible Scholar MCP system guide and instructions",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "get_operation_help",
                "description": "Get help for specific Bible Scholar operations",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "operation_name": {
                            "type": "string",
                            "description": "Name of operation to get help for (optional)"
                        }
                    },
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
                    "tools": True
                },
                "serverInfo": {
                    "name": "bible-scholar-v2",
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
        
        try:
            if tool_name == "quick_database_check":
                result = quick_database_check()
                
            elif tool_name == "quick_server_status":
                result = quick_server_status()
                
            elif tool_name == "quick_hebrew_analysis":
                word = arguments.get('word')
                limit = arguments.get('limit', 10)
                result = quick_hebrew_analysis(word, limit)
                
            elif tool_name == "quick_greek_analysis":
                word = arguments.get('word')
                limit = arguments.get('limit', 10)
                result = quick_greek_analysis(word, limit)
                
            elif tool_name == "quick_verse_search":
                query = arguments.get('query')
                limit = arguments.get('limit', 5)
                result = quick_verse_search(query, limit)
                
            elif tool_name == "quick_lexicon_search":
                term = arguments.get('term')
                language = arguments.get('language', 'both')
                result = quick_lexicon_search(term, language)
                
            elif tool_name == "quick_vector_search":
                query = arguments.get('query')
                limit = arguments.get('limit', 5)
                result = quick_vector_search(query, limit)
                
            elif tool_name == "quick_start_servers":
                result = quick_start_servers()
                
            elif tool_name == "quick_stop_servers":
                result = quick_stop_servers()
                
            elif tool_name == "quick_rule_check":
                rule_type = arguments.get('rule_type', 'all')
                result = quick_rule_check(rule_type)
                
            elif tool_name == "get_system_instructions":
                result = get_system_instructions()
                
            elif tool_name == "get_operation_help":
                operation_name = arguments.get('operation_name')
                result = get_operation_help(operation_name)
                
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Tool {tool_name} not found"
                    }
                }
            
            # Format result as text
            if isinstance(result, dict):
                result_text = json.dumps(result, indent=2)
            else:
                result_text = str(result)
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result_text
                        }
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error executing {tool_name}: {str(e)}"
                        }
                    ]
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
    logger.info("Starting Bible Scholar MCP server...")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Python path: {sys.path}")
    logger.info(f"Python version: {platform.python_version()} ({sys.executable})")
    
    server = BibleScholarMCPServer()
    logger.info(f"Server initialized with {len(server.tools)} tools")
    
    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                logger.info("No input, exiting...")
                break
            
            logger.info(f"[STDIN] Received: {line.strip()}")
            try:
                request = json.loads(line.strip())
                logger.debug(f"Request: {request}")
                
                response = server.handle_request(request)
                logger.info(f"[STDOUT] Responding: {json.dumps(response)}")
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