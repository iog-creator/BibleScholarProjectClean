"""
Type stubs for Bible Scholar MCP Tools
Provides complete type information for IDE support and autocomplete
"""

from typing import Dict, Any, Optional, Union, List

# Quick Functions - Core Operations
def quick_database_check() -> Dict[str, Any]:
    """
    Check database connectivity and basic stats for Hebrew/Greek lexicons
    
    Returns:
        Dict containing database status, connection info, and table counts
    """
    ...

def quick_server_status() -> Dict[str, Any]:
    """
    Check status of all Bible Scholar servers (API, Web UI, LM Studio)
    
    Returns:
        Dict with server status, port information, and health checks
    """
    ...

def quick_hebrew_analysis(word: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
    """
    Analyze Hebrew words with morphology and lexicon data
    
    Args:
        word: Hebrew word to analyze (optional, returns sample if None)
        limit: Maximum number of results to return
    
    Returns:
        Dict containing Hebrew analysis, Strong's numbers, morphology
    """
    ...

def quick_greek_analysis(word: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
    """
    Analyze Greek words with morphology and lexicon data
    
    Args:
        word: Greek word to analyze (optional, returns sample if None)  
        limit: Maximum number of results to return
    
    Returns:
        Dict containing Greek analysis, Strong's numbers, morphology
    """
    ...

def quick_verse_search(query: str, limit: int = 5) -> Dict[str, Any]:
    """
    Search Bible verses across multiple translations
    
    Args:
        query: Search query for Bible verses
        limit: Maximum number of results to return
    
    Returns:
        Dict containing matching verses from multiple translations
    """
    ...

def quick_lexicon_search(term: str, language: str = "both") -> Dict[str, Any]:
    """
    Search Hebrew/Greek lexicon for terms and definitions
    
    Args:
        term: Term to search in lexicon
        language: Language to search ("hebrew", "greek", or "both")
    
    Returns:
        Dict containing lexicon entries, definitions, Strong's numbers
    """
    ...

def quick_vector_search(query: str, limit: int = 5) -> Dict[str, Any]:
    """
    Perform semantic similarity search using vector embeddings
    
    Args:
        query: Query for semantic search
        limit: Maximum number of results to return
    
    Returns:
        Dict containing semantically similar verses with similarity scores
    """
    ...

def quick_start_servers() -> Dict[str, Any]:
    """
    Start Bible Scholar API and Web UI servers
    
    Returns:
        Dict containing startup status and server information
    """
    ...

def quick_stop_servers() -> Dict[str, Any]:
    """
    Stop Bible Scholar API and Web UI servers
    
    Returns:
        Dict containing shutdown status and final server states
    """
    ...

def quick_rule_check(rule_type: str = "all") -> Dict[str, Any]:
    """
    Check compliance with Bible Scholar project rules
    
    Args:
        rule_type: Type of rules to check ("all", "database", "etl", "hebrew", etc.)
    
    Returns:
        Dict containing rule compliance status and any violations
    """
    ...

def get_system_instructions() -> Dict[str, Any]:
    """
    Get comprehensive Bible Scholar MCP system guide and instructions
    
    Returns:
        Dict containing complete system documentation, usage guide, and available operations
    """
    ...

def get_operation_help(operation_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get help for specific Bible Scholar operations
    
    Args:
        operation_name: Name of operation to get help for (optional, shows all if None)
    
    Returns:
        Dict containing detailed help information for specified operation(s)
    """
    ...

# Convenience Aliases - Shorter Names
def db_check() -> Dict[str, Any]:
    """Alias for quick_database_check()"""
    ...

def server_status() -> Dict[str, Any]:
    """Alias for quick_server_status()"""
    ...

def search_verses(query: str, limit: int = 5) -> Dict[str, Any]:
    """Alias for quick_verse_search()"""
    ...

def hebrew_search(word: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
    """Alias for quick_hebrew_analysis()"""
    ...

def greek_search(word: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
    """Alias for quick_greek_analysis()"""
    ...

def help_mcp(operation: Optional[str] = None) -> Dict[str, Any]:
    """Alias for get_operation_help()"""
    ...

# Type aliases for common return structures
BibleVerseResult = Dict[str, Union[str, int, float]]
StrongsEntry = Dict[str, Union[str, int]]
MorphologyEntry = Dict[str, Union[str, int]]
DatabaseStatus = Dict[str, Union[str, int, bool]]
ServerHealth = Dict[str, Union[str, int, bool]]
SearchResults = Dict[str, Union[List[BibleVerseResult], int, str]]

# Export list for __all__
__all__ = [
    'quick_database_check',
    'quick_server_status', 
    'quick_hebrew_analysis',
    'quick_greek_analysis',
    'quick_verse_search',
    'quick_lexicon_search', 
    'quick_vector_search',
    'quick_start_servers',
    'quick_stop_servers',
    'quick_rule_check',
    'get_system_instructions',
    'get_operation_help',
    'db_check',
    'server_status',
    'search_verses', 
    'hebrew_search',
    'greek_search',
    'help_mcp',
    'BibleVerseResult',
    'StrongsEntry', 
    'MorphologyEntry',
    'DatabaseStatus',
    'ServerHealth',
    'SearchResults'
] 