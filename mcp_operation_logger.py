"""
Automatic MCP Operation Logger and Tool Registration System
Critical infrastructure for AI-driven Bible scholarship development

Automatically:
- Logs all successful MCP operations with parameters and results
- Tracks function usage patterns and success rates
- Registers new tools when they work successfully
- Creates documentation for successful operations
- Maintains operation history for learning and debugging
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
import inspect
import functools

class MCPOperationLogger:
    """
    Automatic logger for all MCP operations
    Tracks success, parameters, results, and patterns
    """
    
    def __init__(self, log_dir: str = "logs/mcp_operations"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Log files
        self.success_log = self.log_dir / "successful_operations.jsonl"
        self.error_log = self.log_dir / "failed_operations.jsonl"
        self.tool_registry = self.log_dir / "registered_tools.json"
        self.usage_stats = self.log_dir / "usage_statistics.json"
        
        # Initialize registry if it doesn't exist
        self._initialize_registry()
        
        print(f"[MCP-LOGGER] 📊 Operation logging initialized at {self.log_dir}")
    
    def _initialize_registry(self):
        """Initialize the tool registry with current known tools"""
        if not self.tool_registry.exists():
            initial_tools = {
                "quick_database_check": {
                    "description": "Check database connectivity and basic stats",
                    "parameters": [],
                    "first_success": datetime.now().isoformat(),
                    "success_count": 0,
                    "last_used": None,
                    "category": "database"
                },
                "quick_server_status": {
                    "description": "Check status of all Bible Scholar servers",
                    "parameters": [],
                    "first_success": datetime.now().isoformat(),
                    "success_count": 0,
                    "last_used": None,
                    "category": "system"
                },
                "quick_hebrew_analysis": {
                    "description": "Analyze Hebrew words with morphology",
                    "parameters": ["word", "limit"],
                    "first_success": datetime.now().isoformat(),
                    "success_count": 0,
                    "last_used": None,
                    "category": "analysis"
                },
                "quick_greek_analysis": {
                    "description": "Analyze Greek words with morphology",
                    "parameters": ["word", "limit"],
                    "first_success": datetime.now().isoformat(),
                    "success_count": 0,
                    "last_used": None,
                    "category": "analysis"
                },
                "quick_verse_search": {
                    "description": "Search Bible verses across translations",
                    "parameters": ["query", "limit"],
                    "first_success": datetime.now().isoformat(),
                    "success_count": 0,
                    "last_used": None,
                    "category": "search"
                },
                "quick_lexicon_search": {
                    "description": "Search Hebrew/Greek lexicon",
                    "parameters": ["term", "language"],
                    "first_success": datetime.now().isoformat(),
                    "success_count": 0,
                    "last_used": None,
                    "category": "search"
                },
                "quick_vector_search": {
                    "description": "Semantic similarity search",
                    "parameters": ["query", "limit"],
                    "first_success": datetime.now().isoformat(),
                    "success_count": 0,
                    "last_used": None,
                    "category": "search"
                },
                "quick_start_servers": {
                    "description": "Start Bible Scholar servers",
                    "parameters": [],
                    "first_success": datetime.now().isoformat(),
                    "success_count": 0,
                    "last_used": None,
                    "category": "system"
                },
                "quick_stop_servers": {
                    "description": "Stop Bible Scholar servers",
                    "parameters": [],
                    "first_success": datetime.now().isoformat(),
                    "success_count": 0,
                    "last_used": None,
                    "category": "system"
                },
                "quick_rule_check": {
                    "description": "Check project rule compliance",
                    "parameters": ["rule_type"],
                    "first_success": datetime.now().isoformat(),
                    "success_count": 0,
                    "last_used": None,
                    "category": "validation"
                },
                "get_system_instructions": {
                    "description": "Get comprehensive system guide",
                    "parameters": [],
                    "first_success": datetime.now().isoformat(),
                    "success_count": 0,
                    "last_used": None,
                    "category": "help"
                },
                "get_operation_help": {
                    "description": "Get help for specific operations",
                    "parameters": ["operation_name"],
                    "first_success": datetime.now().isoformat(),
                    "success_count": 0,
                    "last_used": None,
                    "category": "help"
                }
            }
            
            with open(self.tool_registry, 'w') as f:
                json.dump(initial_tools, f, indent=2)
            
            print(f"[MCP-LOGGER] ✅ Initialized tool registry with {len(initial_tools)} tools")
    
    def log_operation(self, operation_name: str, parameters: Dict[str, Any], 
                     result: Any, execution_time: float, success: bool = True):
        """
        Log an operation execution with full details
        
        Args:
            operation_name: Name of the operation/function called
            parameters: Parameters passed to the operation
            result: Result returned by the operation
            execution_time: Time taken to execute in seconds
            success: Whether the operation succeeded
        """
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "operation": operation_name,
            "parameters": parameters,
            "execution_time": execution_time,
            "success": success,
            "result_type": type(result).__name__,
            "result_size": len(str(result)) if result else 0
        }
        
        # Include result for successful operations (truncated if too large)
        if success:
            if isinstance(result, dict) and len(str(result)) < 5000:
                log_entry["result"] = result
            elif len(str(result)) < 1000:
                log_entry["result"] = result
            else:
                log_entry["result_summary"] = str(result)[:500] + "... (truncated)"
        else:
            log_entry["error"] = str(result) if result else "Unknown error"
        
        # Write to appropriate log file
        log_file = self.success_log if success else self.error_log
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        # Update tool registry and stats
        if success:
            self._update_tool_registry(operation_name, parameters, timestamp)
            self._update_usage_stats(operation_name, execution_time)
        
        print(f"[MCP-LOGGER] {'✅' if success else '❌'} {operation_name} "
              f"({execution_time:.3f}s) -> {type(result).__name__}")
    
    def _update_tool_registry(self, operation_name: str, parameters: Dict[str, Any], timestamp: str):
        """Update the tool registry with successful operation"""
        with open(self.tool_registry, 'r') as f:
            registry = json.load(f)
        
        if operation_name not in registry:
            # Auto-register new tool
            param_names = list(parameters.keys()) if parameters else []
            registry[operation_name] = {
                "description": f"Auto-discovered operation: {operation_name}",
                "parameters": param_names,
                "first_success": timestamp,
                "success_count": 1,
                "last_used": timestamp,
                "category": "auto_discovered"
            }
            print(f"[MCP-LOGGER] 🆕 Auto-registered new tool: {operation_name}")
        else:
            # Update existing tool
            registry[operation_name]["success_count"] += 1
            registry[operation_name]["last_used"] = timestamp
        
        with open(self.tool_registry, 'w') as f:
            json.dump(registry, f, indent=2)
    
    def _update_usage_stats(self, operation_name: str, execution_time: float):
        """Update usage statistics"""
        stats_file = self.usage_stats
        
        if stats_file.exists():
            with open(stats_file, 'r') as f:
                stats = json.load(f)
        else:
            stats = {"total_operations": 0, "operations": {}}
        
        stats["total_operations"] += 1
        
        if operation_name not in stats["operations"]:
            stats["operations"][operation_name] = {
                "count": 0,
                "total_time": 0.0,
                "avg_time": 0.0,
                "min_time": execution_time,
                "max_time": execution_time
            }
        
        op_stats = stats["operations"][operation_name]
        op_stats["count"] += 1
        op_stats["total_time"] += execution_time
        op_stats["avg_time"] = op_stats["total_time"] / op_stats["count"]
        op_stats["min_time"] = min(op_stats["min_time"], execution_time)
        op_stats["max_time"] = max(op_stats["max_time"], execution_time)
        
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
    
    def get_tool_registry(self) -> Dict[str, Any]:
        """Get the current tool registry"""
        with open(self.tool_registry, 'r') as f:
            return json.load(f)
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        if self.usage_stats.exists():
            with open(self.usage_stats, 'r') as f:
                return json.load(f)
        return {"total_operations": 0, "operations": {}}
    
    def get_recent_operations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent successful operations"""
        operations = []
        if self.success_log.exists():
            with open(self.success_log, 'r') as f:
                lines = f.readlines()
                for line in reversed(lines[-limit:]):
                    operations.append(json.loads(line.strip()))
        return operations

# Global logger instance
_logger: Optional[MCPOperationLogger] = None

def get_logger() -> MCPOperationLogger:
    """Get the global MCP operation logger"""
    global _logger
    if _logger is None:
        _logger = MCPOperationLogger()
    return _logger

def log_mcp_operation(func: Callable) -> Callable:
    """
    Decorator to automatically log MCP operations
    
    Usage:
        @log_mcp_operation
        def my_mcp_function(param1, param2):
            return result
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger()
        start_time = time.time()
        
        # Get function signature for parameter logging
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.log_operation(
                operation_name=func.__name__,
                parameters=dict(bound_args.arguments),
                result=result,
                execution_time=execution_time,
                success=True
            )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            logger.log_operation(
                operation_name=func.__name__,
                parameters=dict(bound_args.arguments),
                result=e,
                execution_time=execution_time,
                success=False
            )
            
            raise
    
    return wrapper

# Convenience functions for direct logging
def log_success(operation_name: str, parameters: Dict[str, Any], result: Any, execution_time: float):
    """Log a successful operation"""
    get_logger().log_operation(operation_name, parameters, result, execution_time, True)

def log_error(operation_name: str, parameters: Dict[str, Any], error: Exception, execution_time: float):
    """Log a failed operation"""
    get_logger().log_operation(operation_name, parameters, error, execution_time, False)

def get_all_registered_tools() -> Dict[str, Any]:
    """Get all registered tools"""
    return get_logger().get_tool_registry()

def get_operation_stats() -> Dict[str, Any]:
    """Get operation usage statistics"""
    return get_logger().get_usage_stats()

def get_recent_successful_operations(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent successful operations"""
    return get_logger().get_recent_operations(limit)

if __name__ == "__main__":
    # Demo/test the logging system
    logger = get_logger()
    print("MCP Operation Logger initialized and ready!")
    print(f"Registered tools: {len(logger.get_tool_registry())}")
    print(f"Total operations logged: {logger.get_usage_stats().get('total_operations', 0)}") 