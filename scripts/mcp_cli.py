#!/usr/bin/env python3
"""
Bible Scholar MCP Command Line Interface
Provides terminal access to all MCP tools with automatic logging

Usage:
    mcp-cli db-check
    mcp-cli search-verses "love" --limit 10
    mcp-cli hebrew-analysis אהב --limit 5
    mcp-cli greek-analysis ἀγάπη
    mcp-cli vector-search "love and forgiveness" --limit 3
    mcp-cli server-status
    mcp-cli start-servers
    mcp-cli rule-check --type database
    mcp-cli help --operation quick_verse_search
    mcp-cli stats
"""

import argparse
import json
import sys
import os
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_tools import (
    quick_database_check, quick_server_status, quick_hebrew_analysis,
    quick_greek_analysis, quick_verse_search, quick_lexicon_search,
    quick_vector_search, quick_start_servers, quick_stop_servers,
    quick_rule_check, get_system_instructions, get_operation_help,
    get_operation_stats, get_all_registered_tools, get_recent_successful_operations
)

def format_output(result, format_type="pretty"):
    """Format output for display"""
    if format_type == "json":
        return json.dumps(result, indent=2, ensure_ascii=False)
    elif format_type == "compact":
        return json.dumps(result, ensure_ascii=False)
    else:  # pretty format
        if isinstance(result, dict):
            if "status" in result and "message" in result:
                # Status response
                status_icon = "✅" if result.get("success", True) else "❌"
                return f"{status_icon} {result['message']}"
            elif "results" in result and isinstance(result["results"], list):
                # Search results
                output = []
                for i, item in enumerate(result["results"][:10], 1):  # Limit display
                    if "reference" in item and "text" in item:
                        # Bible verse
                        output.append(f"{i}. {item['reference']}: {item['text'][:100]}...")
                    elif "word" in item and "meaning" in item:
                        # Word analysis
                        output.append(f"{i}. {item['word']}: {item.get('meaning', 'N/A')}")
                    else:
                        # Generic result
                        output.append(f"{i}. {str(item)[:100]}...")
                
                total = len(result["results"])
                if total > 10:
                    output.append(f"... and {total - 10} more results")
                
                return "\n".join(output)
            else:
                # Generic dict - show key info
                return json.dumps(result, indent=2, ensure_ascii=False)
        else:
            return str(result)

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Bible Scholar MCP Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s db-check                              # Check database status
  %(prog)s search-verses "love" --limit 5        # Search for verses about love
  %(prog)s hebrew-analysis אהב                   # Analyze Hebrew word for love
  %(prog)s greek-analysis ἀγάπη --limit 3       # Analyze Greek word for love
  %(prog)s lexicon-search "righteousness"        # Search lexicon
  %(prog)s vector-search "forgiveness mercy"     # Semantic search
  %(prog)s server-status                         # Check all servers
  %(prog)s start-servers                         # Start API/Web servers
  %(prog)s rule-check --type hebrew             # Check Hebrew rules
  %(prog)s help --operation quick_verse_search   # Get help for operation
  %(prog)s stats                                 # Show usage statistics
  %(prog)s tools                                 # List all registered tools
        """
    )
    
    # Global options
    parser.add_argument("--format", choices=["pretty", "json", "compact"], 
                       default="pretty", help="Output format")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Verbose output")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Database commands
    subparsers.add_parser("db-check", help="Check database connectivity and stats")
    
    # Server commands
    subparsers.add_parser("server-status", help="Check status of all servers")
    subparsers.add_parser("start-servers", help="Start API and Web UI servers")
    subparsers.add_parser("stop-servers", help="Stop API and Web UI servers")
    
    # Search commands
    search_parser = subparsers.add_parser("search-verses", help="Search Bible verses")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--limit", "-l", type=int, default=5, help="Maximum results")
    
    lexicon_parser = subparsers.add_parser("lexicon-search", help="Search lexicon")
    lexicon_parser.add_argument("term", help="Term to search")
    lexicon_parser.add_argument("--language", choices=["hebrew", "greek", "both"], 
                               default="both", help="Language to search")
    
    vector_parser = subparsers.add_parser("vector-search", help="Semantic similarity search")
    vector_parser.add_argument("query", help="Search query")
    vector_parser.add_argument("--limit", "-l", type=int, default=5, help="Maximum results")
    
    # Analysis commands
    hebrew_parser = subparsers.add_parser("hebrew-analysis", help="Analyze Hebrew words")
    hebrew_parser.add_argument("word", nargs="?", help="Hebrew word to analyze")
    hebrew_parser.add_argument("--limit", "-l", type=int, default=10, help="Maximum results")
    
    greek_parser = subparsers.add_parser("greek-analysis", help="Analyze Greek words")
    greek_parser.add_argument("word", nargs="?", help="Greek word to analyze")
    greek_parser.add_argument("--limit", "-l", type=int, default=10, help="Maximum results")
    
    # Rule commands
    rule_parser = subparsers.add_parser("rule-check", help="Check project rules")
    rule_parser.add_argument("--type", default="all", 
                            help="Rule type (all, database, etl, hebrew, etc.)")
    
    # Help commands
    help_parser = subparsers.add_parser("help", help="Get help for operations")
    help_parser.add_argument("--operation", help="Specific operation to get help for")
    
    subparsers.add_parser("system-info", help="Get comprehensive system information")
    
    # Stats and monitoring commands
    subparsers.add_parser("stats", help="Show usage statistics")
    subparsers.add_parser("tools", help="List all registered tools")
    subparsers.add_parser("recent", help="Show recent operations")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        # Execute the requested command
        if args.command == "db-check":
            result = quick_database_check()
        
        elif args.command == "server-status":
            result = quick_server_status()
        
        elif args.command == "start-servers":
            result = quick_start_servers()
        
        elif args.command == "stop-servers":
            result = quick_stop_servers()
        
        elif args.command == "search-verses":
            result = quick_verse_search(args.query, args.limit)
        
        elif args.command == "lexicon-search":
            result = quick_lexicon_search(args.term, args.language)
        
        elif args.command == "vector-search":
            result = quick_vector_search(args.query, args.limit)
        
        elif args.command == "hebrew-analysis":
            result = quick_hebrew_analysis(args.word, args.limit)
        
        elif args.command == "greek-analysis":
            result = quick_greek_analysis(args.word, args.limit)
        
        elif args.command == "rule-check":
            result = quick_rule_check(args.type)
        
        elif args.command == "help":
            result = get_operation_help(args.operation)
        
        elif args.command == "system-info":
            result = get_system_instructions()
        
        elif args.command == "stats":
            result = get_operation_stats()
        
        elif args.command == "tools":
            result = get_all_registered_tools()
        
        elif args.command == "recent":
            result = get_recent_successful_operations(10)
        
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            return 1
        
        # Format and display output
        output = format_output(result, args.format)
        print(output)
        
        return 0
        
    except Exception as e:
        print(f"Error executing {args.command}: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 