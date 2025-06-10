from flask import Flask, render_template, request, jsonify
import psycopg
from psycopg.rows import dict_row
import requests
import os
import sys
from colorama import Fore, init

init(autoreset=True)

# Add project root to path
project_root = 'C:/Users/mccoy/Documents/Projects/Projects/CursorMCPWorkspace'
sys.path.append(project_root)

from BibleScholarLangChain.scripts.db_config import get_config

app = Flask(__name__, 
    template_folder='templates',
    static_folder='static')

# Get configuration
config = get_config()
API_BASE_URL = 'http://localhost:5000'

def get_db_connection():
    """Create a database connection using psycopg3"""
    print(Fore.CYAN + "Connecting to database...")
    try:
        connection_string = config['database']['connection_string']
        # Fix connection string for psycopg3 (remove +psycopg part)
        if '+psycopg://' in connection_string:
            connection_string = connection_string.replace('postgresql+psycopg://', 'postgresql://')
        conn = psycopg.connect(connection_string, row_factory=dict_row)
        print(Fore.GREEN + "Database connection successful")
        return conn
    except Exception as e:
        print(Fore.RED + f"Connection error: {e}")
        return None

@app.route('/')
def index():
    """Main page"""
    return render_template('search.html')

@app.route('/search')
def search():
    """Search page"""
    return render_template('search.html')

@app.route('/study_dashboard')
def study_dashboard():
    """Study dashboard page"""
    return render_template('study_dashboard.html')

@app.route('/api/search')
def api_search():
    """Proxy search requests to the API server or handle locally"""
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'verse')
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                if search_type == 'verse':
                    cursor.execute(
                        "SELECT book, chapter, verse, text FROM bible.verses WHERE text ILIKE %s LIMIT 10",
                        (f'%{query}%',)
                    )
                    results = cursor.fetchall()
                    return jsonify({'results': results, 'query': query, 'type': search_type})
                else:
                    return jsonify({'results': [], 'query': query, 'type': search_type})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'OK', 'server': 'Web UI Server (port 5002)'})

if __name__ == '__main__':
    print(Fore.GREEN + "Starting simplified Web UI Server on port 5002...")
    app.run(host='0.0.0.0', port=5002, debug=True, use_reloader=False) 