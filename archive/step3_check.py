#!/usr/bin/env python3
"""
Check and fix psycopg2 vs psycopg3 conflicts for BibleScholarLangChain setup
"""
import os
import sys
import subprocess
import json
import requests
import time

# Define paths
project_path = r'C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace\BibleScholarLangChain'
venv_path = r'C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace\BSPclean'

print("Step 3 Check: Testing connections")

# Check if the BSPclean virtual environment exists
if not os.path.exists(os.path.join(venv_path, 'Scripts', 'python.exe')):
    print(f"Error: BSPclean virtual environment not found at {venv_path}")
    sys.exit(1)

# Check if config.json exists
config_path = os.path.join(project_path, 'config', 'config.json')
if not os.path.exists(config_path):
    print(f"Error: config.json not found at {config_path}")
    sys.exit(1)

# Load config.json
try:
    with open(config_path, 'r') as f:
        config = json.load(f)
    print("Successfully loaded config.json")
except Exception as e:
    print(f"Error loading config.json: {e}")
    sys.exit(1)

# Check if LM Studio URL is reachable
lm_studio_url = config.get('api', {}).get('lm_studio_url', 'http://localhost:1234/v1')
try:
    print(f"Testing connection to LM Studio at {lm_studio_url}...")
    response = requests.get(f"{lm_studio_url}/models", timeout=5)
    if response.status_code == 200:
        print(f"LM Studio connection successful: {response.status_code}")
    else:
        print(f"LM Studio connection failed with status code: {response.status_code}")
except Exception as e:
    print(f"Error connecting to LM Studio: {e}")

# Check database connection using psql
db_conn_string = config.get('database', {}).get('connection_string', '')
if 'postgresql' in db_conn_string:
    try:
        # Extract connection details from connection string
        conn_parts = db_conn_string.replace('postgresql+psycopg://', '').split('@')
        if len(conn_parts) == 2:
            auth, host_part = conn_parts
            user_pass = auth.split(':')
            user = user_pass[0]
            host_port_db = host_part.split('/')
            host_port = host_port_db[0].split(':')
            host = host_port[0]
            db = host_port_db[1] if len(host_port_db) > 1 else ''
            
            print(f"Testing database connection to {host}, database {db} as user {user}...")
            
            # Use a simple psql command to test the connection
            cmd = ['psql', '-U', user, '-h', host, '-d', db, '-c', 'SELECT 1']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("Database connection successful")
                print(result.stdout)
            else:
                print("Database connection failed")
                print(result.stderr)
        else:
            print(f"Could not parse connection string: {db_conn_string}")
    except Exception as e:
        print(f"Error testing database connection: {e}")
else:
    print(f"Connection string not in expected format: {db_conn_string}")

print("Step 3 connection checks complete")

def check_and_fix_psycopg():
    """Check if psycopg2 is installed and remove it if found"""
    print("Step 3 Check: Verifying correct psycopg (v3) installation")
    
    # Check installed packages
    result = subprocess.run(
        [os.path.join(venv_path, 'Scripts', 'pip.exe'), 'freeze'], 
        capture_output=True, text=True
    )
    packages = result.stdout.splitlines()
    
    has_psycopg2 = False
    has_psycopg3 = False
    
    for pkg in packages:
        if pkg.startswith('psycopg2'):
            has_psycopg2 = True
            print(f"Found psycopg2 package: {pkg}")
        if pkg.startswith('psycopg=='):
            has_psycopg3 = True
            print(f"Found psycopg3 package: {pkg}")
    
    # Take action if needed
    if has_psycopg2:
        print("Issue detected: psycopg2 is installed, which conflicts with psycopg3")
        print("Uninstalling psycopg2...")
        subprocess.run(
            [os.path.join(venv_path, 'Scripts', 'pip.exe'), 'uninstall', '-y', 'psycopg2', 'psycopg2-binary'], 
            capture_output=True, text=True
        )
    
    if not has_psycopg3:
        print("Issue detected: psycopg3 is not installed")
        print("Installing psycopg3...")
    
    if has_psycopg2 or not has_psycopg3:
        print("Ensuring psycopg3 (v3.1.8) is installed...")
        subprocess.run(
            [os.path.join(venv_path, 'Scripts', 'pip.exe'), 'install', 'psycopg==3.1.8'], 
            capture_output=True, text=True
        )
        
        # Verify the fix
        result = subprocess.run(
            [os.path.join(venv_path, 'Scripts', 'python.exe'), '-c', 
             "import psycopg; print(f'Psycopg version: {psycopg.__version__}')"], 
            capture_output=True, text=True
        )
        print(result.stdout)
        
        # Also check if langchain-postgres is installed
        result = subprocess.run(
            [os.path.join(venv_path, 'Scripts', 'python.exe'), '-c', 
             "from langchain_postgres.vectorstores import PGVector; print('PGVector import successful')"], 
            capture_output=True, text=True
        )
        if "PGVector import successful" in result.stdout:
            print("PGVector import successful")
        else:
            print("Warning: PGVector import failed, installing langchain-postgres...")
            subprocess.run(
                [os.path.join(venv_path, 'Scripts', 'pip.exe'), 'install', 'langchain-postgres==0.0.13'], 
                capture_output=True, text=True
            )
    else:
        print("Environment check passed: psycopg3 is installed and psycopg2 is not present")
    
    return True

def check_vector_tables():
    """Check if LangChain PGVector tables exist"""
    print("\nChecking if LangChain PGVector tables exist...")
    try:
        # Use the virtual environment's Python to check
        check_cmd = [
            os.path.join(venv_path, 'Scripts', 'python.exe'),
            '-c',
            """
import psycopg
conn = psycopg.connect("postgresql://postgres:postgres@localhost:5432/bible_db")
with conn:
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('langchain_pg_collection')")
        collection_exists = cur.fetchone()[0] is not None
        cur.execute("SELECT to_regclass('langchain_pg_embedding')")
        embedding_exists = cur.fetchone()[0] is not None
        print(f"Collection table exists: {collection_exists}")
        print(f"Embedding table exists: {embedding_exists}")
        if collection_exists and embedding_exists:
            cur.execute("SELECT COUNT(*) FROM langchain_pg_collection WHERE name = 'bible_verses'")
            collection_count = cur.fetchone()[0]
            print(f"Bible verses collection exists: {collection_count > 0}")
            if collection_count > 0:
                cur.execute("SELECT COUNT(*) FROM langchain_pg_embedding WHERE collection_id = (SELECT uuid FROM langchain_pg_collection WHERE name = 'bible_verses')")
                embedding_count = cur.fetchone()[0]
                print(f"Bible verses embedding count: {embedding_count}")
            """
        ]
        
        result = subprocess.run(check_cmd, capture_output=True, text=True)
        print(result.stdout)
        
        if "Bible verses collection exists: True" in result.stdout:
            print("Vector tables check passed: Tables exist and bible_verses collection is present")
            return True
        else:
            print("Vector tables check failed: Will create tables in the next step")
            return False
    except Exception as e:
        print(f"Error checking vector tables: {e}")
        return False

if __name__ == "__main__":
    psycopg_fixed = check_and_fix_psycopg()
    tables_exist = check_vector_tables()
    
    if psycopg_fixed:
        print("\nPsycopg3 environment check completed successfully")
    else:
        print("\nWarning: Psycopg3 environment check encountered issues")
    
    if tables_exist:
        print("LangChain PGVector tables already exist, no creation needed")
    else:
        print("LangChain PGVector tables need to be created in the next step")
    
    sys.exit(0 if psycopg_fixed else 1) 