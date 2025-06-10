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