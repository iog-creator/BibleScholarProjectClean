"""
Comprehensive Search API for BibleScholarLangChain.

This API provides enhanced Bible search capabilities by integrating:
- LangChain PGVector store (using existing database tables)
- Native pgvector semantic search
- Cross-references from versification mappings
- Hebrew/Greek word analysis
- Multi-translation support with comprehensive ranking

The system utilizes the existing database structure including:
- public.langchain_pg_collection
- public.langchain_pg_embedding  
- bible.verse_embeddings
- bible.versification_mappings
- bible.hebrew_ot_words / bible.greek_nt_words
"""

from flask import Blueprint, request, jsonify
import logging
import sys
import os
from typing import Dict, Any

# Add the project root to path for imports
sys.path.append('C:\\Users\\mccoy\\Documents\\Projects\\Projects\\CursorMCPWorkspace')

try:
    from BibleScholarLangChain.src.database.langchain_integration import BibleLangChainStore
    LANGCHAIN_INTEGRATION_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("LangChain integration successfully imported")
except ImportError as e:
    # Try alternative import path
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from src.database.langchain_integration import BibleLangChainStore
        LANGCHAIN_INTEGRATION_AVAILABLE = True
        logger = logging.getLogger(__name__)
        logger.info("LangChain integration successfully imported (alternative path)")
    except ImportError as e2:
        logging.warning(f"LangChain integration not available: {e} / {e2}")
        BibleLangChainStore = None
        LANGCHAIN_INTEGRATION_AVAILABLE = False

# Create Blueprint for comprehensive search API
comprehensive_search_api = Blueprint('comprehensive_search', __name__)

# Initialize the LangChain store
langchain_store = None
if LANGCHAIN_INTEGRATION_AVAILABLE:
    try:
        langchain_store = BibleLangChainStore()
        logger.info("BibleLangChainStore initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize BibleLangChainStore: {e}")

@comprehensive_search_api.route('/status', methods=['GET'])
def status():
    """Status endpoint for comprehensive search API."""
    return jsonify({
        "status": "ok",
        "message": "Comprehensive Search API is running",
        "langchain_integration_available": LANGCHAIN_INTEGRATION_AVAILABLE,
        "store_initialized": langchain_store is not None,
        "features": [
            "LangChain vector search",
            "Native pgvector search", 
            "Cross-reference mapping",
            "Hebrew/Greek word analysis",
            "Multi-translation support",
            "Intelligent result ranking"
        ],
        "database_tables": [
            "public.langchain_pg_collection",
            "public.langchain_pg_embedding",
            "bible.verse_embeddings", 
            "bible.versification_mappings",
            "bible.hebrew_ot_words",
            "bible.greek_nt_words"
        ]
    })

@comprehensive_search_api.route('/search', methods=['POST'])
def comprehensive_search():
    """
    Perform comprehensive Bible search using all available data sources.
    
    JSON Body:
    {
        "query": "love one another",
        "translation": "KJV",
        "k": 10,
        "include_cross_refs": true,
        "include_word_analysis": true
    }
    
    Returns comprehensive search results with multiple data sources.
    """
    try:
        if not langchain_store:
            return jsonify({
                "error": "Comprehensive search not available - LangChain integration missing",
                "available": False
            }), 503
        
        # Parse request
        data = request.get_json()
        query = data.get('query', '')
        translation = data.get('translation', 'KJV')
        k = data.get('k', 10)
        include_cross_refs = data.get('include_cross_refs', True)
        include_word_analysis = data.get('include_word_analysis', True)
        
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400
        
        # Perform comprehensive search
        results = langchain_store.comprehensive_search(
            query=query,
            translation=translation,
            k=k,
            include_cross_refs=include_cross_refs,
            include_word_analysis=include_word_analysis
        )
        
        if not results.get('combined_results'):
            return jsonify({"error": "Sorry, I can only answer using the Bible database. No answer found for your query."}), 404
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error in comprehensive search: {e}")
        return jsonify({"error": str(e)}), 500

@comprehensive_search_api.route('/populate', methods=['POST'])
def populate_langchain_store():
    """
    Populate the LangChain store with Bible verses.
    This would typically be used for initial setup or updates.
    """
    try:
        if not langchain_store:
            return jsonify({
                "error": "LangChain store not available",
                "available": False
            }), 503
        
        # Get parameters
        data = request.get_json() or {}
        translation = data.get('translation', 'KJV') 
        batch_size = data.get('batch_size', 100)
        
        # This would implement population logic
        # For now, return a placeholder response
        return jsonify({
            "message": "Population functionality not yet implemented",
            "translation": translation,
            "batch_size": batch_size,
            "status": "placeholder"
        })
        
    except Exception as e:
        logger.error(f"Error populating store: {e}")
        return jsonify({"error": str(e)}), 500

@comprehensive_search_api.route('/store-stats', methods=['GET'])
def store_statistics():
    """Get comprehensive statistics about the LangChain store and database resources."""
    try:
        if not langchain_store:
            return jsonify({
                "error": "LangChain store not available",
                "available": False
            }), 503
        
        stats = langchain_store.get_store_status()
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting store statistics: {e}")
        return jsonify({"error": str(e)}), 500

@comprehensive_search_api.route('/health', methods=['GET'])
def health_check():
    """Detailed health check for all comprehensive search components."""
    try:
        health_status = {
            "status": "ok",
            "timestamp": "2025-01-18T12:00:00Z",
            "components": {
                "api": "healthy",
                "langchain_integration": "healthy" if LANGCHAIN_INTEGRATION_AVAILABLE else "unavailable",
                "langchain_store": "healthy" if langchain_store else "unavailable"
            },
            "capabilities": {
                "comprehensive_search": langchain_store is not None,
                "vector_search": True,
                "cross_references": True,
                "word_analysis": True,
                "multi_translation": True
            }
        }
        
        # Test store status if available
        if langchain_store:
            try:
                store_status = langchain_store.get_store_status()
                health_status["store_statistics"] = store_status.get("statistics", {})
                health_status["database_coverage"] = store_status.get("coverage", {})
            except Exception as e:
                health_status["components"]["langchain_store"] = f"error: {str(e)}"
                health_status["capabilities"]["comprehensive_search"] = False
        
        return jsonify(health_status)
        
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "components": {
                "api": "error",
                "langchain_integration": "unknown",
                "langchain_store": "unknown"
            }
        }), 500

@comprehensive_search_api.route('/search/simple', methods=['GET'])
def simple_search():
    """
    Simple search endpoint with query parameters for easy testing.
    
    Query Parameters:
    - q: Search query
    - translation: Bible translation (default: KJV)
    - limit: Number of results (default: 10)
    """
    try:
        if not langchain_store:
            return jsonify({
                "error": "Comprehensive search not available",
                "available": False
            }), 503
        
        query = request.args.get('q', '')
        translation = request.args.get('translation', 'KJV')
        limit = min(int(request.args.get('limit', 10)), 50)
        
        if not query:
            return jsonify({"error": "Query parameter 'q' is required"}), 400
        
        # Perform comprehensive search
        results = langchain_store.comprehensive_search(
            query=query,
            translation=translation,
            k=limit,
            include_cross_refs=False,  # Simplified for basic search
            include_word_analysis=False
        )
        
        if not results.get('combined_results'):
            return jsonify({"error": "Sorry, I can only answer using the Bible database. No answer found for your query."}), 404
        
        # Return simplified format
        simplified_results = {
            "query": query,
            "translation": translation,
            "results": results.get("combined_results", []),
            "total_results": len(results.get("combined_results", [])),
            "processing_time_ms": results.get("metadata", {}).get("processing_time_ms", 0),
            "sources_used": results.get("metadata", {}).get("sources_used", [])
        }
        
        return jsonify(simplified_results)
        
    except Exception as e:
        logger.error(f"Error in simple search: {e}")
        return jsonify({"error": str(e)}), 500

@comprehensive_search_api.route('/translations', methods=['GET'])
def available_translations():
    """Get list of available Bible translations."""
    try:
        # This would query the database for available translations
        # For now, return the standard set
        translations = {
            "available_translations": [
                {"code": "KJV", "name": "King James Version"},
                {"code": "ASV", "name": "American Standard Version"}, 
                {"code": "YLT", "name": "Young's Literal Translation"},
                {"code": "TAHOT", "name": "The Ancient Hebrew Old Testament"}
            ],
            "default": "KJV",
            "notes": "Translation availability depends on database content"
        }
        
        return jsonify(translations)
        
    except Exception as e:
        logger.error(f"Error getting translations: {e}")
        return jsonify({"error": str(e)}), 500

# Error handlers
@comprehensive_search_api.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": [
            "/status",
            "/search",
            "/search/simple", 
            "/populate",
            "/store-stats",
            "/health",
            "/translations"
        ]
    }), 404

@comprehensive_search_api.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred in the comprehensive search API"
    }), 500 