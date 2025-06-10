#!/usr/bin/env python3
"""
Main API server for BibleScholarLangChain
Registers all API blueprints and serves on port 5000
"""
from flask import Flask, jsonify
from flask_caching import Cache
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Import and register blueprints
from BibleScholarLangChain.src.api.contextual_insights_api import contextual_insights_bp

# Import comprehensive search API
try:
    from BibleScholarLangChain.src.api.comprehensive_search import comprehensive_search_api
    app.register_blueprint(comprehensive_search_api, url_prefix='/api/comprehensive')
    COMPREHENSIVE_SEARCH_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Comprehensive search API not available: {e}")
    COMPREHENSIVE_SEARCH_AVAILABLE = False

app.register_blueprint(contextual_insights_bp, url_prefix='/api/contextual_insights')

# Placeholder blueprints for other APIs
from flask import Blueprint

# Vector Search API placeholder
vector_search_bp = Blueprint('vector_search', __name__)

@vector_search_bp.route('/vector-search', methods=['POST'])
def vector_search():
    return jsonify({'status': 'Vector search API - coming soon'})

@vector_search_bp.route('/health')
def vector_search_health():
    return jsonify({'status': 'ok', 'server': 'Vector Search API'})

app.register_blueprint(vector_search_bp, url_prefix='/api/vector_search')

# Lexicon API placeholder
lexicon_bp = Blueprint('lexicon', __name__)

@lexicon_bp.route('/search')
def lexicon_search():
    return jsonify({'status': 'Lexicon search API - coming soon'})

@lexicon_bp.route('/health')
def lexicon_health():
    return jsonify({'status': 'ok', 'server': 'Lexicon API'})

app.register_blueprint(lexicon_bp, url_prefix='/api/lexicon')

# Search API placeholder
search_bp = Blueprint('search', __name__)

@search_bp.route('/search')
def search():
    return jsonify({'status': 'Search API - coming soon'})

@search_bp.route('/health')
def search_health():
    return jsonify({'status': 'ok', 'server': 'Search API'})

app.register_blueprint(search_bp, url_prefix='/api')

# Cross Language API placeholder
cross_language_bp = Blueprint('cross_language', __name__)

@cross_language_bp.route('/csv')
def cross_language_csv():
    return jsonify({'status': 'Cross-language API - coming soon'})

@cross_language_bp.route('/health')
def cross_language_health():
    return jsonify({'status': 'ok', 'server': 'Cross Language API'})

app.register_blueprint(cross_language_bp, url_prefix='/api/cross_language')

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'server': 'API Server (port 5000)'})

@app.route('/')
def index():
    endpoints = [
        '/api/contextual_insights/insights',
        '/api/contextual_insights/health',
        '/api/contextual_insights/test_lm_studio',
        '/api/vector_search/vector-search',
        '/api/lexicon/search',
        '/api/search',
        '/api/cross_language/csv',
        '/health'
    ]
    
    # Add comprehensive search endpoints if available
    if COMPREHENSIVE_SEARCH_AVAILABLE:
        endpoints.extend([
            '/api/comprehensive/status',
            '/api/comprehensive/search',
            '/api/comprehensive/search/simple',
            '/api/comprehensive/store-stats',
            '/api/comprehensive/health',
            '/api/comprehensive/translations'
        ])
    
    return jsonify({
        'name': 'BibleScholarLangChain API',
        'version': '1.0.0',
        'features': {
            'comprehensive_search': COMPREHENSIVE_SEARCH_AVAILABLE,
            'langchain_integration': COMPREHENSIVE_SEARCH_AVAILABLE,
            'database_tables': [
                'public.langchain_pg_collection',
                'public.langchain_pg_embedding',
                'bible.verse_embeddings',
                'bible.versification_mappings',
                'bible.hebrew_ot_words',
                'bible.greek_nt_words'
            ] if COMPREHENSIVE_SEARCH_AVAILABLE else []
        },
        'endpoints': endpoints
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False) 