import os
import subprocess
import json
import time

# Define paths
project_path = r'C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace\BibleScholarLangChain'
venv_path = r'C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace\BSPclean'
log_path = r'C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace\logs\setup.log'

# Uninstall psycopg2 if it exists to avoid conflicts
print("Checking for and removing psycopg2 to avoid conflicts...")
try:
    result = subprocess.run([os.path.join(venv_path, 'Scripts', 'pip.exe'), 'freeze'], capture_output=True, text=True)
    if 'psycopg2' in result.stdout:
        print("Found psycopg2 installation, removing...")
        subprocess.run([os.path.join(venv_path, 'Scripts', 'pip.exe'), 'uninstall', '-y', 'psycopg2', 'psycopg2-binary'], capture_output=True, text=True)
        print("Reinstalling psycopg3...")
        subprocess.run([os.path.join(venv_path, 'Scripts', 'pip.exe'), 'install', 'psycopg==3.1.8'], capture_output=True, text=True)
    else:
        print("No psycopg2 installation found, continuing with psycopg3")
except Exception as e:
    print(f"Error checking pip packages: {e}")

print("Step 3: Setting up vector store with LangChain")

# Write load_bible_data.py
load_bible_data_content = """
import os
import requests
import time
from langchain_postgres.vectorstores import PGVector
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from scripts.db_config import get_config
from src.database.database import get_db_connection
from colorama import Fore, init

init(autoreset=True)

class LMStudioEmbedding(Embeddings):
    def __init__(self, url, model):
        self.url = url
        self.model = model

    def embed_documents(self, texts):
        print(Fore.CYAN + f"Generating embeddings for {len(texts)} texts...")
        headers = {"Content-Type": "application/json"}
        data = {"model": self.model, "input": texts}
        try:
            response = requests.post(self.url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            embeddings = [item['embedding'] for item in response.json()['data']]
            print(Fore.GREEN + f"Generated {len(embeddings)} embeddings")
            return embeddings
        except Exception as e:
            print(Fore.RED + f"Embedding error: {e}")
            raise

    def embed_query(self, text):
        return self.embed_documents([text])[0]

def load_bible_data():
    print(Fore.CYAN + "Loading Bible data into PGVector...")
    config = get_config()
    
    # Check if LM Studio is accessible
    embeddings_url = os.getenv("LM_STUDIO_EMBEDDINGS_URL", "http://localhost:1234/v1/embeddings")
    embeddings_model = os.getenv("LM_STUDIO_EMBEDDING_MODEL", "bge-m3")
    
    print(Fore.CYAN + f"Testing connection to LM Studio at {embeddings_url}...")
    try:
        base_url = embeddings_url.split('/embeddings')[0]
        response = requests.get(f"{base_url}/models", timeout=5)
        if response.status_code != 200:
            print(Fore.RED + f"LM Studio connection failed: {response.status_code}")
            return
        print(Fore.GREEN + "LM Studio connection successful")
    except Exception as e:
        print(Fore.RED + f"Error connecting to LM Studio: {e}")
        return
    
    # Connect to the database
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
    except Exception as e:
        print(Fore.RED + f"Database connection error: {e}")
        return
    
    # Limited to 10 verses initially for testing
    try:
        cursor.execute("SELECT book_name, chapter_num, verse_num, verse_text, translation_source, id FROM bible.verses WHERE translation_source IN ('KJV', 'ASV') LIMIT 10")
        verses = cursor.fetchall()
        if not verses:
            print(Fore.YELLOW + "No verses found in the database")
            cursor.close()
            conn.close()
            return
        print(Fore.GREEN + f"Retrieved {len(verses)} verses from database")
    except Exception as e:
        print(Fore.RED + f"Database query error: {e}")
        cursor.close()
        conn.close()
        return
    
    cursor.close()
    conn.close()

    documents = [
        Document(
            page_content=verse[3],
            metadata={"book": verse[0], "chapter": verse[1], "verse": verse[2], "translation": verse[4], "verse_id": verse[5]}
        )
        for verse in verses
    ]
    ids = [f"{verse[0]}_{verse[1]}_{verse[2]}_{verse[4]}" for verse in verses]

    embeddings = LMStudioEmbedding(embeddings_url, embeddings_model)
    
    try:
        # First try to create the tables if they don't exist
        print(Fore.CYAN + "Creating PGVector tables if they don't exist...")
        PGVector.create_tables(
            connection_string=config['database']['connection_string'],
            collection_name="bible_verses",
            embedding_length=config['vector_search']['embedding_length']
        )
        print(Fore.GREEN + "Tables created or already exist")
        
        # Initialize the vector store
        vector_store = PGVector(
            embeddings=embeddings,
            connection=config['database']['connection_string'],
            collection_name="bible_verses",
            use_jsonb=True,
            embedding_length=config['vector_search']['embedding_length']
        )
        
        # Add documents
        print(Fore.CYAN + f"Adding {len(documents)} documents to vector store...")
        vector_store.add_documents(documents, ids=ids)
        print(Fore.GREEN + f"Successfully loaded {len(documents)} verses into PGVector")
        
        # Test similarity search
        print(Fore.CYAN + "Testing similarity search...")
        results = vector_store.similarity_search("love", k=2)
        print(Fore.GREEN + f"Search successful, found {len(results)} results")
        for doc in results:
            print(f"- {doc.page_content}")
            
        return True
    except Exception as e:
        print(Fore.RED + f"Error in vector store operations: {e}")
        return False

if __name__ == "__main__":
    load_bible_data()
"""
with open(os.path.join(project_path, 'src', 'utils', 'load_bible_data.py'), 'w') as f:
    f.write(load_bible_data_content.strip())
print('Created load_bible_data.py')

# Create __init__.py files to make imports work
init_files = [
    os.path.join(project_path, 'src', '__init__.py'),
    os.path.join(project_path, 'src', 'api', '__init__.py'),
    os.path.join(project_path, 'src', 'database', '__init__.py'),
    os.path.join(project_path, 'src', 'utils', '__init__.py'),
    os.path.join(project_path, 'scripts', '__init__.py')
]
for init_file in init_files:
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            f.write('# Init file for imports')
        print(f'Created {init_file}')

# Test vector store with timeout
def run_with_timeout(cmd, timeout=60):
    print(f"Running command with {timeout} second timeout...")
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Poll process for new output until finished or timeout
        start_time = time.time()
        output = []
        error_output = []
        
        while process.poll() is None:
            # Check if timeout exceeded
            if time.time() - start_time > timeout:
                process.terminate()
                print(f"Process timed out after {timeout} seconds")
                return False, "".join(output), "Timeout exceeded"
            
            # Get output if available
            stdout_line = process.stdout.readline()
            if stdout_line:
                print(stdout_line.strip())
                output.append(stdout_line)
            
            stderr_line = process.stderr.readline()
            if stderr_line:
                print(f"ERROR: {stderr_line.strip()}")
                error_output.append(stderr_line)
                
            time.sleep(0.1)
        
        # Get remaining output
        remaining_stdout, remaining_stderr = process.communicate()
        if remaining_stdout:
            print(remaining_stdout)
            output.append(remaining_stdout)
        if remaining_stderr:
            print(f"ERROR: {remaining_stderr}")
            error_output.append(remaining_stderr)
        
        success = process.returncode == 0
        return success, "".join(output), "".join(error_output)
    except Exception as e:
        print(f"Error running command: {e}")
        return False, "", str(e)

# Check if BSPclean environment exists
if os.path.exists(os.path.join(venv_path, 'Scripts', 'python.exe')):
    print("Testing vector store...")
    
    # Test loading Bible data
    cmd = [
        os.path.join(venv_path, 'Scripts', 'python.exe'),
        '-c',
        f"""
import os, sys
os.environ['PYTHONPATH'] = r'{project_path}'
sys.path.append(r'{project_path}')
try:
    from src.utils.load_bible_data import load_bible_data
    success = load_bible_data()
    if success:
        print('Vector store setup complete')
    else:
        print('Vector store setup failed')
except Exception as e:
    print(f'Vector store error: {{e}}')
"""
    ]
    
    success, output, error = run_with_timeout(cmd, timeout=90)
    
    if success:
        print("Vector store setup completed successfully")
    else:
        print(f"Vector store setup failed: {error}")

    # Verify vector store data if psql is available
    try:
        # Load config to get connection details
        with open(os.path.join(project_path, 'config', 'config.json'), 'r') as f:
            config = json.load(f)
        
        # Extract db details
        db_conn_string = config.get('database', {}).get('connection_string', '')
        if 'postgresql' in db_conn_string:
            conn_parts = db_conn_string.replace('postgresql+psycopg://', '').split('@')
            if len(conn_parts) == 2:
                auth, host_part = conn_parts
                user_pass = auth.split(':')
                user = user_pass[0]
                host_port_db = host_part.split('/')
                db = host_port_db[1] if len(host_port_db) > 1 else ''
                
                print(f"Verifying vector store data in database {db}...")
                result = subprocess.run(['psql', '-U', user, '-d', db, '-c', 
                                        "SELECT COUNT(*) FROM langchain_pg_embedding WHERE collection_id = (SELECT uuid FROM langchain_pg_collection WHERE name = 'bible_verses');"], 
                                       capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print('Vector store count:', result.stdout)
                else:
                    print('Error checking vector store count:', result.stderr)
    except Exception as e:
        print(f'Error verifying vector store data: {e}')

    # Log action if possible
    try:
        print("Logging action...")
        log_cmd = [
            os.path.join(venv_path, 'Scripts', 'python.exe'),
            '-c',
            f"""
import os, sys
os.environ['PYTHONPATH'] = r'{project_path}'
sys.path.append(r'C:/Users/mccoy/Documents/Projects/Projects/CursorMCPWorkspace')
try:
    from scripts.log_user_interactions import log_action
    log_action('Set up vector store', 'C:/Users/mccoy/Documents/Projects/Projects/CursorMCPWorkspace/logs/setup.log')
    print('Logged action successfully')
except Exception as e:
    print(f'Logging error: {{e}}')
"""
        ]
        success, output, error = run_with_timeout(log_cmd, timeout=10)
        if success:
            print("Logging completed successfully")
        else:
            print(f"Logging failed: {error}")
            
        if os.path.exists('C:/Users/mccoy/Documents/Projects/Projects/CursorMCPWorkspace/logs/setup.log'):
            with open('C:/Users/mccoy/Documents/Projects/Projects/CursorMCPWorkspace/logs/setup.log', 'r') as f:
                print('Setup log:', f.read())
        else:
            print('Log file not created yet')
    except Exception as e:
        print(f'Warning: MCP logging failed: {e}')
else:
    print('Skipping vector store test: virtual environment not found')

print("Step 3 completed") 