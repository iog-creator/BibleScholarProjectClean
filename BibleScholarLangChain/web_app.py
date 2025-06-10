#!/usr/bin/env python3
"""
Web UI server for BibleScholarLangChain
Enhanced with LM Studio integration and comprehensive Bible study features
Serves the user interface on port 5002 and provides direct LM Studio access
"""
import os
import sys
import json
import logging
import requests
import tempfile
from flask import Flask, flash, render_template, request, redirect, url_for, session, jsonify
from flask_caching import Cache
from dotenv import load_dotenv, set_key
from logging.handlers import RotatingFileHandler
import datetime
import shutil

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv(dotenv_path='.env')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key_change_in_production')

# Cache configuration
ENABLE_CACHE = os.getenv('ENABLE_CACHE', '0').lower() in ['1', 'true', 'yes']
if ENABLE_CACHE:
    app.config['CACHE_TYPE'] = 'SimpleCache'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300
    cache = Cache(app)
else:
    cache = None

# Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000')
LM_STUDIO_URL = 'http://localhost:1234/v1'

# --- LOGGING CONFIGURATION ---
def get_log_file_handler(log_file_path):
    try:
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        return RotatingFileHandler(log_file_path, maxBytes=102400, backupCount=1, encoding='utf-8')
    except PermissionError:
        temp_log = tempfile.NamedTemporaryFile(delete=False, suffix='.log')
        print(f"[WARNING] Log file {log_file_path} is locked. Using temporary log file: {temp_log.name}")
        return RotatingFileHandler(temp_log.name, maxBytes=102400, backupCount=1, encoding='utf-8')

# Setup logging
log_file_path = os.path.join('logs', 'web_app.log')
file_handler = get_log_file_handler(log_file_path)
file_handler.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)

class SuppressNoiseFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        if 'change detected' in msg or 'watchfiles' in record.name:
            return False
        return True

file_handler.addFilter(SuppressNoiseFilter())
console_handler.addFilter(SuppressNoiseFilter())
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler],
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.info(f"[web_app.py] API_BASE_URL loaded: {API_BASE_URL}")
logger.info(f"[web_app.py] LM Studio URL: {LM_STUDIO_URL}")

# --- UTILITY FUNCTIONS ---

def reload_env():
    """Reload environment variables from .env file"""
    load_dotenv(dotenv_path='.env', override=True)
    global API_BASE_URL, LM_STUDIO_URL
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000')
    LM_STUDIO_URL = 'http://localhost:1234/v1'

def get_model_settings():
    """Get current model settings from environment variables"""
    return {
        'enable_thinking': os.getenv('QWEN_ENABLE_THINKING', 'false').lower() in ['1', 'true', 'yes'],
        'temperature': float(os.getenv('QWEN_TEMPERATURE_GENERAL', 0.7)),
        'top_p': float(os.getenv('QWEN_TOP_P_GENERAL', 0.95)),
        'top_k': int(os.getenv('QWEN_TOP_K_GENERAL', 20)),
        'min_p': float(os.getenv('QWEN_MIN_P_GENERAL', 0.0)),
    }

def test_lm_studio_connection():
    """Test connection to LM Studio"""
    try:
        response = requests.get(f"{LM_STUDIO_URL}/models", timeout=5)
        if response.status_code == 200:
            models = response.json()
            logger.info(f"LM Studio connection successful. Available models: {models}")
            return True, models
        else:
            logger.error(f"LM Studio connection failed with status: {response.status_code}")
            return False, None
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to connect to LM Studio: {e}")
        return False, None

def query_lm_studio_direct(prompt, max_tokens=4096, temperature=0.7):
    """Direct query to LM Studio for testing and fallback"""
    try:
        payload = {
            "model": "meta-llama-3.1-8b-instruct",  # Default model
            "messages": [
                {"role": "system", "content": "You are a Bible study assistant. You must only answer questions using the data available in the bible_db database. Do not use your own knowledge, outside sources, or make up content. If the answer is not in the database, respond: 'Sorry, I can only answer using the Bible database. No answer found for your query.'"},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }
        
        response = requests.post(
            f"{LM_STUDIO_URL}/chat/completions",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content']
        else:
            logger.error(f"Unexpected LM Studio response format: {result}")
            return "Error: Unexpected response format from LM Studio"
            
    except Exception as e:
        logger.error(f"Error querying LM Studio: {e}")
        return f"Error connecting to LM Studio: {str(e)}"

def proxy_api_request(endpoint, params=None, json_data=None, method='GET', timeout=30):
    """Enhanced proxy requests to the API server with better error handling"""
    try:
        if method.upper() == 'POST':
            response = requests.post(f"{API_BASE_URL}{endpoint}", params=params, json=json_data, timeout=timeout)
        else:
            response = requests.get(f"{API_BASE_URL}{endpoint}", params=params, timeout=timeout)
        return response.json(), response.status_code
    except requests.exceptions.Timeout:
        return {'error': f'API request timed out after {timeout}s'}, 504
    except requests.exceptions.ConnectionError:
        return {'error': 'Cannot connect to API server. Make sure it is running on port 5000.'}, 503
    except Exception as e:
        return {'error': f'API request failed: {str(e)}'}, 500

# --- ROUTES ---

@app.route('/')
def index():
    """Home page with navigation to main features"""
    return render_template('search.html')

@app.route('/search')
def search():
    """Bible verse search page"""
    return render_template('search.html')

@app.route('/dashboard')
@app.route('/study_dashboard')
def study_dashboard():
    """Study dashboard with various tools"""
    return render_template('study_dashboard.html')

@app.route('/test-lm-studio')
def test_lm_studio():
    """Test LM Studio connection and display results"""
    logger.info("Testing LM Studio connection...")
    
    # Test basic connection
    is_connected, models = test_lm_studio_connection()
    
    test_results = {
        'connection_status': 'Connected' if is_connected else 'Disconnected',
        'models': models if models else [],
        'lm_studio_url': LM_STUDIO_URL,
        'test_timestamp': datetime.datetime.now().isoformat()
    }
    
    # Test a simple query if connected
    if is_connected:
        try:
            test_prompt = "What is the meaning of John 3:16?"
            test_response = query_lm_studio_direct(test_prompt)
            test_results['test_query'] = test_prompt
            test_results['test_response'] = test_response
            test_results['query_status'] = 'Success'
        except Exception as e:
            test_results['query_status'] = 'Failed'
            test_results['query_error'] = str(e)
    
    return render_template('test_lm_studio.html', results=test_results)

@app.route('/contextual-insights', methods=['GET', 'POST'])
def contextual_insights():
    """Advanced contextual insights interface"""
    if request.method == 'POST':
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            focus_type = data.get('type', 'text_snippet')
            reference = data.get('reference', '')
            topic = data.get('query_text', '')
            snippet = data.get('text', '')
        else:
            focus_type = request.form.get('focus_type', 'text_snippet')
            reference = request.form.get('reference', '')
            topic = request.form.get('topic', '')
            snippet = request.form.get('snippet', '')
        
        # Prepare input data
        input_data = {'type': focus_type}
        if focus_type == 'verse':
            input_data['reference'] = reference
            query_text = reference
        elif focus_type == 'topic':
            input_data['query_text'] = topic
            query_text = topic
        else:
            input_data['text'] = snippet
            query_text = snippet
        
        if not query_text:
            error = "Please provide a query, reference, or text snippet."
            return render_template('contextual_insights.html', error=error)
        
        # Add model settings
        model_settings = get_model_settings()
        input_data.update(model_settings)
        
        try:
            # Try API first
            data, status_code = proxy_api_request('/api/contextual_insights/insights', 
                                                json_data=input_data, method='POST', timeout=120)
            
            if status_code == 200 and 'insights' in data:
                insights = data['insights']
                error = None
            else:
                # Fallback to direct LM Studio
                logger.warning(f"API failed with status {status_code}, trying direct LM Studio query")
                prompt = f"Provide detailed biblical insights for: {query_text}"
                lm_response = query_lm_studio_direct(prompt)
                insights = {
                    'summary': lm_response,
                    'source': 'Direct LM Studio (API fallback)',
                    'query_type': focus_type
                }
                error = None
                
        except Exception as e:
            logger.error(f"Both API and LM Studio failed: {e}")
            insights = None
            error = f"Error: {str(e)}"
        
        return render_template('contextual_insights.html', 
                             input_data=input_data, 
                             insights=insights, 
                             error=error)
    
    # GET request
    return render_template('contextual_insights.html')

@app.route('/tutor', methods=['GET', 'POST'])
def tutor():
    """Bible Scholar Tutor interface"""
    if request.method == 'POST':
        try:
            # Import the tutor module
            from bible_scholar_tutor import BibleScholarTutor
            
            query = request.form.get('query', '') if not request.is_json else request.get_json().get('query', '')
            if not query:
                return jsonify({'error': 'Query is required'}), 400
            
            tutor = BibleScholarTutor()
            verses = tutor.search_verses(query)
            insights = tutor.get_insights(query, verses)
            
            if request.is_json:
                return jsonify({'verses': verses, 'insights': insights})
            else:
                return render_template('tutor.html', query=query, verses=verses, insights=insights)
                
        except ImportError:
            error = "Bible Scholar Tutor module not available"
            if request.is_json:
                return jsonify({'error': error}), 500
            else:
                return render_template('tutor.html', error=error)
        except Exception as e:
            error = f"Tutor error: {str(e)}"
            if request.is_json:
                return jsonify({'error': error}), 500
            else:
                return render_template('tutor.html', error=error)
    
    return render_template('tutor.html')

# --- API PROXY ROUTES ---

@app.route('/api/search')
def api_search():
    """Enhanced search with 30s timeout"""
    params = {
        'q': request.args.get('q', ''),
        'type': request.args.get('type', 'verse')
    }
    data, status_code = proxy_api_request('/api/search', params, timeout=30)
    return jsonify(data), status_code

@app.route('/api/lexicon/search')
def api_lexicon_search():
    params = {
        'term': request.args.get('term', ''),
        'strong_id': request.args.get('strong_id', ''),
        'limit': request.args.get('limit', '10')
    }
    data, status_code = proxy_api_request('/api/lexicon/search', params)
    return jsonify(data), status_code

@app.route('/api/vector_search/vector-search')
def api_vector_search():
    params = {
        'q': request.args.get('q', ''),
        'limit': request.args.get('limit', '5'),
        'threshold': request.args.get('threshold', '0.7')
    }
    data, status_code = proxy_api_request('/api/vector_search/vector-search', params)
    return jsonify(data), status_code

@app.route('/api/contextual_insights/insights', methods=['GET', 'POST'])
def api_contextual_insights():
    if request.method == 'POST':
        data, status_code = proxy_api_request('/api/contextual_insights/insights', 
                                            json_data=request.get_json(), method='POST', timeout=120)
    else:
        params = {
            'query': request.args.get('query', ''),
            'context': request.args.get('context', '')
        }
        data, status_code = proxy_api_request('/api/contextual_insights/insights', params)
    return jsonify(data), status_code

@app.route('/api/cross_language/csv')
def api_cross_language():
    data, status_code = proxy_api_request('/api/cross_language/csv')
    return jsonify(data), status_code

@app.route('/api/lm-studio/direct', methods=['POST'])
def lm_studio_direct_api():
    """Direct API endpoint for LM Studio queries"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        max_tokens = data.get('max_tokens', 4096)
        temperature = data.get('temperature', 0.7)
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        response = query_lm_studio_direct(prompt, max_tokens, temperature)
        
        return jsonify({
            'response': response,
            'status': 'success',
            'timestamp': datetime.datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Direct LM Studio API error: {e}")
        return jsonify({'error': str(e)}), 500

# --- SETTINGS ROUTES ---

@app.route('/save-model-settings', methods=['POST'])
def save_model_settings():
    """Save model settings to environment file"""
    try:
        data = request.get_json()
        env_path = '.env'
        
        # Backup .env file
        backup_path = env_path + '.bak_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        if os.path.exists(env_path):
            shutil.copy(env_path, backup_path)
        
        # Update values
        set_key(env_path, 'QWEN_ENABLE_THINKING', str(data.get('enable_thinking', False)).lower())
        set_key(env_path, 'QWEN_TEMPERATURE_GENERAL', str(data.get('temperature', 0.7)))
        set_key(env_path, 'QWEN_TOP_P_GENERAL', str(data.get('top_p', 0.95)))
        set_key(env_path, 'QWEN_TOP_K_GENERAL', str(data.get('top_k', 20)))
        set_key(env_path, 'QWEN_MIN_P_GENERAL', str(data.get('min_p', 0.0)))
        
        reload_env()
        return jsonify({'message': 'Settings saved and reloaded successfully.'})
        
    except Exception as e:
        logger.error(f"Error saving model settings: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get-model-settings')
def get_model_settings_route():
    """Get current model settings"""
    try:
        settings = get_model_settings()
        return jsonify(settings)
    except Exception as e:
        logger.error(f"Error getting model settings: {e}")
        return jsonify({'error': str(e)}), 500

# --- HEALTH AND STATUS ---

@app.route('/health')
def health():
    """Enhanced health check for both web UI and API servers"""
    # Check API server
    try:
        api_response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        api_status = "accessible" if api_response.status_code == 200 else "not responding"
    except:
        api_status = "not accessible"
    
    # Check LM Studio
    lm_connected, lm_models = test_lm_studio_connection()
    lm_status = "connected" if lm_connected else "not accessible"
    
    return jsonify({
        'status': 'OK', 
        'server': 'Web UI Server (port 5002)',
        'api_server_status': api_status,
        'api_status': api_status,
        'lm_studio_status': lm_status,
        'api_base_url': API_BASE_URL,
        'lm_studio_url': LM_STUDIO_URL,
        'timestamp': datetime.datetime.now().isoformat()
    })

# --- ERROR HANDLERS ---

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error="Internal server error"), 500

if __name__ == '__main__':
    try:
        logger.info("Starting Bible Scholar Web Application...")
        logger.info(f"API Base URL: {API_BASE_URL}")
        logger.info(f"LM Studio URL: {LM_STUDIO_URL}")
        
        # Test LM Studio connection on startup
        is_connected, models = test_lm_studio_connection()
        if is_connected:
            logger.info("✓ LM Studio connection successful")
        else:
            logger.warning("⚠ LM Studio not accessible - some features may not work")
        
        print("Starting Web UI Server on port 5002...")
        print(f"Proxying API requests to: {API_BASE_URL}")
        print(f"LM Studio integration: {LM_STUDIO_URL}")
        app.run(host='0.0.0.0', port=5002, debug=True, use_reloader=False)
    except Exception as e:
        logger.error(f"Failed to start web application: {e}")
        raise 