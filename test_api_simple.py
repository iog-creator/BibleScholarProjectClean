#!/usr/bin/env python3
"""
Simple test API server with only the enhanced Contextual Insights API
"""
from flask import Flask
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'BibleScholarLangChain'))

app = Flask(__name__)

# Import and register only the contextual insights blueprint
from BibleScholarLangChain.src.api.contextual_insights_api import contextual_insights_bp

app.register_blueprint(contextual_insights_bp, url_prefix='/api/contextual_insights')

@app.route('/health')
def health():
    return {'status': 'ok', 'server': 'Simple Test API Server (port 5000)'}

@app.route('/')
def index():
    return {
        'name': 'Simple Test API for Enhanced Contextual Insights',
        'version': '1.0.0',
        'endpoints': [
            '/api/contextual_insights/insights',
            '/api/contextual_insights/health',
            '/health'
        ]
    }

if __name__ == '__main__':
    print("Starting simple test API server...")
    app.run(host='0.0.0.0', port=5200, debug=True, use_reloader=False) 