import os
import subprocess

# Define paths
project_path = r'C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace\BibleScholarLangChain'
venv_path = r'C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace\BSPclean'
log_path = r'C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace\logs\setup.log'

# Write load_bible_data.py
load_bible_data_content = """
import os
import requests
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
            response = requests.post(self.url, headers=headers, json=data, timeout=10)
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
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT book_name, chapter_num, verse_num, verse_text, translation_source, id FROM bible.verses WHERE translation_source IN ('KJV', 'ASV') LIMIT 100") # Limited for testing
    verses = cursor.fetchall()
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

    # Get LMStudio URL from config
    embeddings_url = os.getenv("LM_STUDIO_EMBEDDINGS_URL", "http://localhost:1234/v1/embeddings")
    embeddings_model = os.getenv("LM_STUDIO_EMBEDDING_MODEL", "bge-m3")
    
    embeddings = LMStudioEmbedding(embeddings_url, embeddings_model)
    
    vector_store = PGVector(
        embeddings=embeddings,
        connection=config['database']['connection_string'],
        collection_name="bible_verses",
        use_jsonb=True,
        embedding_length=config['vector_search']['embedding_length']
    )

    try:
        vector_store.add_documents(documents, ids=ids)
        print(Fore.GREEN + f"Loaded {len(documents)} verses into PGVector")
    except Exception as e:
        print(Fore.RED + f"Error loading data: {e}")
        # Try creating the tables first in case they don't exist
        try:
            print(Fore.YELLOW + "Attempting to create tables...")
            PGVector.create_tables(config['database']['connection_string'], collection_name="bible_verses", embedding_length=config['vector_search']['embedding_length'])
            vector_store.add_documents(documents, ids=ids)
            print(Fore.GREEN + f"Created tables and loaded {len(documents)} verses into PGVector")
        except Exception as inner_e:
            print(Fore.RED + f"Failed to create tables: {inner_e}")
            raise

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
    with open(init_file, 'w') as f:
        f.write('# Init file for imports')
    print(f'Created {init_file}')

# Test vector store if possible
try:
    if os.path.exists(os.path.join(venv_path, 'Scripts', 'python.exe')):
        print("Testing vector store...")
        cmd = [
            os.path.join(venv_path, 'Scripts', 'python.exe'),
            '-c',
            f"""
import os, sys
os.environ['PYTHONPATH'] = r'{project_path}'
sys.path.append(r'{project_path}')
try:
    from src.utils.load_bible_data import load_bible_data
    load_bible_data()
    print('Vector store test complete')
except Exception as e:
    print(f'Vector store error: {{e}}')
"""
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)
    else:
        print('Skipping vector store test: virtual environment not found')
except Exception as e:
    print(f'Error testing vector store: {e}')

# Verify vector store data
try:
    result = subprocess.run(['psql', '-U', 'postgres', '-d', 'bible_db', '-c', "SELECT COUNT(*) FROM langchain_pg_embedding WHERE collection_id = (SELECT uuid FROM langchain_pg_collection WHERE name = 'bible_verses');"], capture_output=True, text=True)
    print('Vector store count:', result.stdout)
except Exception as e:
    print(f'Error checking vector store count: {e}')

# Log action if possible
try:
    if os.path.exists(os.path.join(venv_path, 'Scripts', 'python.exe')):
        cmd = [
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
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        
        log_path = 'C:/Users/mccoy/Documents/Projects/Projects/CursorMCPWorkspace/logs/setup.log'
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                print('Setup log:', f.read())
        else:
            print('Log file not created yet')
    else:
        print('Skipping logging: virtual environment not found')
except Exception as e:
    print(f'Warning: MCP logging failed: {e}') 