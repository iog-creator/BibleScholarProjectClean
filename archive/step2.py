import os
import shutil
import subprocess

# Define paths
project_path = r'C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace\BibleScholarLangChain'
venv_path = r'C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace\BSPclean'
log_path = r'C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace\logs\setup.log'

# Create directories
dirs = [
    os.path.join(project_path, 'src', 'api'),
    os.path.join(project_path, 'src', 'database'),
    os.path.join(project_path, 'src', 'utils'),
    os.path.join(project_path, 'scripts'),
    os.path.join(project_path, 'config'),
    os.path.join(project_path, 'templates'),
    os.path.join(project_path, 'static', 'js'),
    os.path.join(project_path, 'static', 'css')
]
for d in dirs:
    os.makedirs(d, exist_ok=True)
print('Created directory structure')

# Write config.json
config_content = '''
{
  "database": {
    "connection_string": "postgresql+psycopg://postgres:postgres@localhost:5432/bible_db"
  },
  "api": {
    "lm_studio_url": "http://localhost:1234/v1"
  },
  "vector_search": {
    "embedding_model": "bge-m3",
    "embedding_length": 1024
  },
  "defaults": {
    "model": "meta-llama-3.1-8b-instruct"
  }
}
'''
with open(os.path.join(project_path, 'config', 'config.json'), 'w') as f:
    f.write(config_content.strip())
print('Created config.json')

# Write .env
env_content = '''
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bible_db
DB_USER=postgres
DB_PASSWORD=postgres
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/bible_db
LM_STUDIO_EMBEDDING_MODEL=bge-m3
LM_STUDIO_EMBEDDINGS_URL=http://localhost:1234/v1/embeddings
'''
with open(os.path.join(project_path, '.env'), 'w') as f:
    f.write(env_content.strip())
print('Created .env')

# Write db_config.py with proper path handling
db_config_content = """
import os
import json
from dotenv import load_dotenv
from colorama import Fore, init

init(autoreset=True)
load_dotenv()

def get_config():
    print(Fore.CYAN + "Loading configuration...")
    config_path = "C:/Users/mccoy/Documents/Projects/Projects/CursorMCPWorkspace/BibleScholarLangChain/config/config.json"
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(Fore.GREEN + "Configuration loaded successfully")
        return config
    except Exception as e:
        print(Fore.RED + f"Config error: {e}")
        raise RuntimeError("Failed to load config.json")

def get_db_url():
    print(Fore.CYAN + "Loading database URL...")
    url = os.getenv("DATABASE_URL")
    if url:
        print(Fore.GREEN + f"Database URL: {url}")
        return url
    config = get_config()
    url = config['database']['connection_string']
    print(Fore.GREEN + f"Database URL from config: {url}")
    return url
"""
with open(os.path.join(project_path, 'scripts', 'db_config.py'), 'w') as f:
    f.write(db_config_content.strip())
print('Created db_config.py')

# Write database.py
database_content = """
from sqlalchemy import create_engine
from scripts.db_config import get_db_url
from colorama import Fore, init

init(autoreset=True)

def get_db_connection():
    print(Fore.CYAN + "Connecting to database...")
    try:
        url = get_db_url()
        engine = create_engine(url)
        conn = engine.connect()
        print(Fore.GREEN + "Database connection successful")
        return conn
    except Exception as e:
        print(Fore.RED + f"Connection error: {e}")
        raise
"""
with open(os.path.join(project_path, 'src', 'database', 'database.py'), 'w') as f:
    f.write(database_content.strip())
print('Created database.py')

# Copy UI files if they exist
ui_files = [
    (r'C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace\BibleScholarProjectv2\templates\study_dashboard.html', os.path.join(project_path, 'templates', 'study_dashboard.html')),
    (r'C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace\BibleScholarProjectv2\static\js\dashboard.js', os.path.join(project_path, 'static', 'js', 'dashboard.js')),
    (r'C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace\BibleScholarProjectv2\static\css\dashboard.css', os.path.join(project_path, 'static', 'css', 'dashboard.css'))
]
for src, dst in ui_files:
    if os.path.exists(src):
        shutil.copy(src, dst)
        print(f'Copied: {os.path.basename(src)}')
    else:
        print(f'Warning: {src} not found')

# Create a basic dashboard template if original not found
if not os.path.exists(os.path.join(project_path, 'templates', 'study_dashboard.html')):
    basic_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bible Study Dashboard</title>
        <link rel="stylesheet" href="/static/css/dashboard.css">
    </head>
    <body>
        <div class="container">
            <h1>Bible Study Dashboard</h1>
            <div class="search-section">
                <h2>Contextual Insights</h2>
                <input type="text" id="reference-input" placeholder="Enter Bible reference (e.g., John 3:16)">
                <button id="search-button">Get Insights</button>
            </div>
            <div id="results-section">
                <div id="loading" style="display: none;">Loading...</div>
                <div id="insights-results"></div>
            </div>
        </div>
        <script src="/static/js/dashboard.js"></script>
    </body>
    </html>
    """
    with open(os.path.join(project_path, 'templates', 'study_dashboard.html'), 'w') as f:
        f.write(basic_template.strip())
    print('Created basic study_dashboard.html template')

# Create basic JS if original not found
if not os.path.exists(os.path.join(project_path, 'static', 'js', 'dashboard.js')):
    basic_js = """
    document.addEventListener('DOMContentLoaded', function() {
        const searchButton = document.getElementById('search-button');
        const referenceInput = document.getElementById('reference-input');
        const insightsResults = document.getElementById('insights-results');
        const loading = document.getElementById('loading');
        
        searchButton.addEventListener('click', function() {
            const reference = referenceInput.value.trim();
            if (!reference) return;
            
            loading.style.display = 'block';
            insightsResults.innerHTML = '';
            
            fetch('/api/contextual_insights/insights', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    type: 'verse',
                    reference: reference
                })
            })
            .then(response => response.json())
            .then(data => {
                loading.style.display = 'none';
                
                if (data.error) {
                    insightsResults.innerHTML = `<div class="error">${data.error}</div>`;
                    return;
                }
                
                const insights = data.insights;
                let html = `
                    <div class="insight-card">
                        <h3>Summary</h3>
                        <p>${insights.summary || 'No summary available'}</p>
                    </div>
                `;
                
                if (insights.theological_terms && Object.keys(insights.theological_terms).length > 0) {
                    html += `
                        <div class="insight-card">
                            <h3>Theological Terms</h3>
                            <ul>
                    `;
                    
                    for (const [term, definition] of Object.entries(insights.theological_terms)) {
                        html += `<li><strong>${term}</strong>: ${definition}</li>`;
                    }
                    
                    html += `
                            </ul>
                        </div>
                    `;
                }
                
                if (insights.cross_references && insights.cross_references.length > 0) {
                    html += `
                        <div class="insight-card">
                            <h3>Cross References</h3>
                            <ul>
                    `;
                    
                    for (const ref of insights.cross_references) {
                        html += `<li><strong>${ref.reference}</strong>: ${ref.text} (${ref.reason})</li>`;
                    }
                    
                    html += `
                            </ul>
                        </div>
                    `;
                }
                
                if (insights.historical_context) {
                    html += `
                        <div class="insight-card">
                            <h3>Historical Context</h3>
                            <p>${insights.historical_context}</p>
                        </div>
                    `;
                }
                
                insightsResults.innerHTML = html;
            })
            .catch(error => {
                loading.style.display = 'none';
                insightsResults.innerHTML = `<div class="error">Error: ${error.message}</div>`;
            });
        });
    });
    """
    with open(os.path.join(project_path, 'static', 'js', 'dashboard.js'), 'w') as f:
        f.write(basic_js.strip())
    print('Created basic dashboard.js')

# Create basic CSS if original not found
if not os.path.exists(os.path.join(project_path, 'static', 'css', 'dashboard.css')):
    basic_css = """
    body {
        font-family: Arial, sans-serif;
        line-height: 1.6;
        margin: 0;
        padding: 0;
        background-color: #f5f5f5;
    }
    
    .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }
    
    h1 {
        color: #333;
        text-align: center;
    }
    
    .search-section {
        background-color: #fff;
        padding: 20px;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    
    input[type="text"] {
        width: 70%;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 16px;
    }
    
    button {
        padding: 10px 20px;
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 16px;
    }
    
    button:hover {
        background-color: #45a049;
    }
    
    #results-section {
        background-color: #fff;
        padding: 20px;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }
    
    .insight-card {
        margin-bottom: 20px;
        padding: 15px;
        border-left: 4px solid #4CAF50;
        background-color: #f9f9f9;
    }
    
    .insight-card h3 {
        margin-top: 0;
        color: #333;
    }
    
    .error {
        color: #f44336;
        font-weight: bold;
    }
    """
    with open(os.path.join(project_path, 'static', 'css', 'dashboard.css'), 'w') as f:
        f.write(basic_css.strip())
    print('Created basic dashboard.css')

# Test file structure
files = [
    os.path.join(project_path, 'config', 'config.json'),
    os.path.join(project_path, '.env'),
    os.path.join(project_path, 'scripts', 'db_config.py'),
    os.path.join(project_path, 'src', 'database', 'database.py'),
    os.path.join(project_path, 'templates', 'study_dashboard.html')
]
for f in files:
    if os.path.exists(f):
        print(f'File: {f}, Size: {os.path.getsize(f)} bytes')
    else:
        print(f'Error: {f} missing')

# Test database connection with the BSPclean Python executable
try:
    if os.path.exists(os.path.join(venv_path, 'Scripts', 'python.exe')):
        result = subprocess.run(
            [os.path.join(venv_path, 'Scripts', 'python.exe'), 
             '-c', 
             f"import os, sys; os.environ['PYTHONPATH'] = r'{project_path}'; sys.path.append(r'{project_path}'); from src.database.database import get_db_connection; get_db_connection()"], 
            capture_output=True, 
            text=True
        )
        print(result.stdout)
    else:
        print('Skipping database connection test: virtual environment not found')
except Exception as e:
    print(f'Error testing database connection: {e}')

# Log action if possible
try:
    if os.path.exists(os.path.join(venv_path, 'Scripts', 'python.exe')):
        subprocess.run(
            [os.path.join(venv_path, 'Scripts', 'python.exe'), 
             '-c', 
             f"import os, sys; os.environ['PYTHONPATH'] = r'{project_path}'; sys.path.append(r'C:/Users/mccoy/Documents/Projects/Projects/CursorMCPWorkspace'); from scripts.log_user_interactions import log_action; log_action('Created minimal file structure', '{log_path}')"], 
            check=True
        )
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                print('Setup log:', f.read())
        else:
            print('Log file not created yet')
    else:
        print('Skipping logging: virtual environment not found')
except Exception as e:
    print(f'Warning: MCP logging failed: {e}') 