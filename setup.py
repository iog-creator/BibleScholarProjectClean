#!/usr/bin/env python3
"""
BibleScholarLangChain Setup Script
This script replaces setup.ipynb due to notebook format issues.
"""

import os
import sys
import shutil
import subprocess
import json
import time
from pathlib import Path

# Define paths using forward slashes
project_path = "C:/Users/mccoy/Documents/Projects/Projects/CursorMCPWorkspace/BibleScholarLangChain"
venv_path = "C:/Users/mccoy/Documents/Projects/Projects/CursorMCPWorkspace/BSPclean"
log_path = "C:/Users/mccoy/Documents/Projects/Projects/CursorMCPWorkspace/logs/setup.log"

def log_action(message):
    """Log an action to the setup log file"""
    subprocess.run([
        os.path.join(venv_path, 'Scripts', 'python.exe'),
        '-c',
        f"from C:/Users/mccoy/Documents/Projects/Projects/CursorMCPWorkspace/scripts/log_user_interactions import log_action; log_action('{message}', '{log_path}')"
    ], check=True)

def create_directory_structure():
    """Step 1: Create project directory structure"""
    print("Creating directory structure...")
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

def create_config_files():
    """Step 2: Create configuration files"""
    print("Creating configuration files...")
    
    # Write config.json
    config = {
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
    with open(os.path.join(project_path, 'config', 'config.json'), 'w') as f:
        json.dump(config, f, indent=2)
    print('Created config.json')

    # Write .env
    env_content = """
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bible_db
DB_USER=postgres
DB_PASSWORD=postgres
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/bible_db
LM_STUDIO_EMBEDDING_MODEL=bge-m3
LM_STUDIO_EMBEDDINGS_URL=http://localhost:1234/v1/embeddings
"""
    with open(os.path.join(project_path, '.env'), 'w') as f:
        f.write(env_content.strip())
    print('Created .env')

def create_database_files():
    """Step 3: Create database access files"""
    print("Creating database files...")
    
    # Write db_config.py
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
from C:/Users/mccoy/Documents/Projects/Projects/CursorMCPWorkspace/BibleScholarLangChain/scripts/db_config import get_db_url
from colorama import Fore, init

init(autoreset=True)

def get_db_connection():
    """Create a database connection using SQLAlchemy (used for legacy components)"""
    print(Fore.CYAN + "Connecting to database using SQLAlchemy...")
    try:
        url = get_db_url()
        engine = create_engine(url)
        conn = engine.connect()
        print(Fore.GREEN + "SQLAlchemy database connection successful")
        return conn
    except Exception as e:
        print(Fore.RED + f"Connection error: {e}")
        raise
"""
    with open(os.path.join(project_path, 'src', 'database', 'database.py'), 'w') as f:
        f.write(database_content.strip())
    print('Created database.py')

    # Write secure_connection.py
    secure_connection_content = """
import psycopg
from psycopg.rows import dict_row
from C:/Users/mccoy/Documents/Projects/Projects/CursorMCPWorkspace/BibleScholarLangChain/scripts/db_config import get_db_url
from colorama import Fore, init

init(autoreset=True)

def get_secure_connection():
    """Create a secure database connection using psycopg3"""
    print(Fore.CYAN + "Creating secure database connection...")
    try:
        url = get_db_url()
        conn = psycopg.connect(url, row_factory=dict_row)
        print(Fore.GREEN + "Secure database connection successful")
        return conn
    except Exception as e:
        print(Fore.RED + f"Connection error: {e}")
        raise
"""
    with open(os.path.join(project_path, 'src', 'database', 'secure_connection.py'), 'w') as f:
        f.write(secure_connection_content.strip())
    print('Created secure_connection.py')

def copy_ui_files():
    """Step 4: Copy UI files from v2"""
    print("Copying UI files...")
    ui_files = [
        ("C:/Users/mccoy/Documents/Projects/Projects/CursorMCPWorkspace/BibleScholarProjectv2/templates/study_dashboard.html", 
         os.path.join(project_path, 'templates', 'study_dashboard.html')),
        ("C:/Users/mccoy/Documents/Projects/Projects/CursorMCPWorkspace/BibleScholarProjectv2/static/js/dashboard.js",
         os.path.join(project_path, 'static', 'js', 'dashboard.js')),
        ("C:/Users/mccoy/Documents/Projects/Projects/CursorMCPWorkspace/BibleScholarProjectv2/static/css/dashboard.css",
         os.path.join(project_path, 'static', 'css', 'dashboard.css'))
    ]
    for src, dst in ui_files:
        if os.path.exists(src):
            shutil.copy(src, dst)
            print(f'Copied: {os.path.basename(src)}')
        else:
            print(f'Warning: {src} not found')

def verify_files():
    """Step 5: Verify file structure"""
    print("Verifying file structure...")
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

def test_database():
    """Step 6: Test database connection"""
    print("Testing database connection...")
    result = subprocess.run(
        [os.path.join(venv_path, 'Scripts', 'python.exe'),
         '-c',
         f"import os; os.environ['PYTHONPATH'] = '{project_path}'; from src.database.database import get_db_connection; get_db_connection()"],
        capture_output=True,
        text=True
    )
    print(result.stdout)

def main():
    """Main setup process"""
    try:
        print("Starting BibleScholarLangChain setup...")
        
        # Execute setup steps
        create_directory_structure()
        log_action('Created directory structure')
        
        create_config_files()
        log_action('Created configuration files')
        
        create_database_files()
        log_action('Created database files')
        
        copy_ui_files()
        log_action('Copied UI files')
        
        verify_files()
        log_action('Verified file structure')
        
        test_database()
        log_action('Tested database connection')
        
        print("\nSetup completed successfully!")
        
    except Exception as e:
        print(f"Error during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 