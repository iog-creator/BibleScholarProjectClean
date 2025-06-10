import os
import json
import subprocess
import time

# Define paths
project_path = r'C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace\BibleScholarLangChain'
venv_path = r'C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace\BSPclean'

print("Step 3: Setting up LangChain PGVector tables")

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

# Create a direct SQL script to create the PGVector tables
sql_script_content = """
import os
import json
import psycopg

# Get database connection string from config
def get_db_connection_string():
    config_path = "C:/Users/mccoy/Documents/Projects/Projects/CursorMCPWorkspace/BibleScholarLangChain/config/config.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config['database']['connection_string']

# Create the PGVector tables directly with SQL commands
def create_pgvector_tables():
    print("Creating PGVector tables for LangChain via direct SQL...")
    conn_string = get_db_connection_string()
    
    try:
        # Connect to the database
        conn = psycopg.connect(conn_string)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create vector extension if it doesn't exist
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # Create the tables that LangChain PGVector would create
        # Based on langchain-postgres 0.0.13 implementation
        
        # Create collection table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS langchain_pg_collection (
            uuid UUID PRIMARY KEY,
            name VARCHAR(50) UNIQUE,
            cmetadata JSONB
        );
        ''')
        
        # Create embedding table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS langchain_pg_embedding (
            uuid UUID PRIMARY KEY,
            collection_id UUID REFERENCES langchain_pg_collection(uuid) ON DELETE CASCADE,
            embedding vector(1024),
            document JSONB,
            cmetadata JSONB,
            custom_id VARCHAR(100)
        );
        ''')
        
        # Create index on collection name
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_langchain_pg_collection_name
        ON langchain_pg_collection (name);
        ''')
        
        # Create index on embedding collection_id
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_langchain_pg_embedding_collection_id
        ON langchain_pg_embedding (collection_id);
        ''')
        
        # Create index on custom_id
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_langchain_pg_embedding_custom_id
        ON langchain_pg_embedding (custom_id);
        ''')
        
        # Create the collection for bible verses if it doesn't exist
        cursor.execute('''
        INSERT INTO langchain_pg_collection (uuid, name, cmetadata)
        VALUES (gen_random_uuid(), 'bible_verses', '{}')
        ON CONFLICT (name) DO NOTHING;
        ''')
        
        # Create vector index for similarity search
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS langchain_pg_embedding_vector_idx 
        ON langchain_pg_embedding 
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
        ''')
        
        # Close the connection
        cursor.close()
        conn.close()
        
        print("PGVector tables created successfully")
        return True
    except Exception as e:
        print(f"Error creating PGVector tables: {e}")
        return False

if __name__ == "__main__":
    create_pgvector_tables()
"""

with open(os.path.join(project_path, 'src', 'utils', 'create_pgvector_tables_sql.py'), 'w') as f:
    f.write(sql_script_content.strip())
print('Created create_pgvector_tables_sql.py')

# Create necessary __init__.py files
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

# Run a simplified test to just create tables
if os.path.exists(os.path.join(venv_path, 'Scripts', 'python.exe')):
    print("Creating PGVector tables using direct SQL...")
    
    try:
        create_cmd = [
            os.path.join(venv_path, 'Scripts', 'python.exe'),
            os.path.join(project_path, 'src', 'utils', 'create_pgvector_tables_sql.py')
        ]
        
        print("Running SQL table creation...")
        result = subprocess.run(create_cmd, capture_output=True, text=True, timeout=60)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        # Also verify if tables were created
        verify_cmd = [
            "psql", "-U", "postgres", "-d", "bible_db", "-c",
            "SELECT COUNT(*) FROM langchain_pg_collection WHERE name = 'bible_verses';"
        ]
        verify_result = subprocess.run(verify_cmd, capture_output=True, text=True)
        print("Verification result:", verify_result.stdout)
        
        print("Step 3 completed with direct SQL table creation")
    except Exception as e:
        print(f"Error during table creation: {e}")
else:
    print("Skipping table creation: virtual environment not found")

# Add a simpler API version to confirm collection creation
api_version_content = """
from langchain_postgres.vectorstores import PGVector
from langchain_core.embeddings import Embeddings

class DummyEmbeddings(Embeddings):
    def embed_documents(self, texts):
        return [[0.1] * 1024 for _ in texts]
        
    def embed_query(self, text):
        return [0.1] * 1024

def confirm_pgvector_setup():
    connection_string = "postgresql://postgres:postgres@localhost:5432/bible_db"
    
    try:
        # Just create an instance without trying to create tables
        embeddings = DummyEmbeddings()
        vector_store = PGVector(
            embeddings=embeddings,
            connection=connection_string,
            collection_name="bible_verses",
            embedding_length=1024
        )
        
        # Get the collection to confirm it exists
        collection = vector_store.get_collection()
        return True, f"Collection exists: {collection}"
    except Exception as e:
        return False, f"Error confirming setup: {e}"

if __name__ == "__main__":
    success, message = confirm_pgvector_setup()
    print(f"Success: {success}")
    print(f"Message: {message}")
"""

with open(os.path.join(project_path, 'src', 'utils', 'confirm_pgvector.py'), 'w') as f:
    f.write(api_version_content.strip())
print('Created confirm_pgvector.py')

# Run the confirmation script
if os.path.exists(os.path.join(venv_path, 'Scripts', 'python.exe')):
    print("Confirming PGVector setup...")
    
    try:
        confirm_cmd = [
            os.path.join(venv_path, 'Scripts', 'python.exe'),
            os.path.join(project_path, 'src', 'utils', 'confirm_pgvector.py')
        ]
        
        print("Running confirmation...")
        result = subprocess.run(confirm_cmd, capture_output=True, text=True, timeout=30)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
    except Exception as e:
        print(f"Error during confirmation: {e}")

print("Step 3 tables setup completed") 