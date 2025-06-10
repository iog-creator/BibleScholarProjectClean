#!/usr/bin/env python3
"""
Database configuration module for BibleScholarLangChain
"""
import json
import os
from typing import Dict, Any

def load_config() -> Dict[str, Any]:
    """Load configuration from config.json"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Override with environment variables if available
    if os.getenv('DATABASE_URL'):
        config['database']['connection_string'] = os.getenv('DATABASE_URL')
    
    if os.getenv('LM_STUDIO_BASE_URL'):
        config['lm_studio']['base_url'] = os.getenv('LM_STUDIO_BASE_URL')
    
    return config

def get_database_url() -> str:
    """Get database connection string"""
    config = load_config()
    return config['database']['connection_string']

def get_lm_studio_config() -> Dict[str, Any]:
    """Get LM Studio configuration"""
    config = load_config()
    return config['lm_studio']

def get_server_config() -> Dict[str, Any]:
    """Get server configuration"""
    config = load_config()
    return config['server']