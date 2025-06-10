import os
import json
import psycopg
from langchain_postgres.vectorstores import PGVector
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

# Get database connection string from config
def get_db_connection_string():
    config_path = "C:/Users/mccoy/Documents/Projects/Projects/CursorMCPWorkspace/BibleScholarLangChain/config/config.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config['database']['connection_string']

# Simple placeholder embedding class
class DummyEmbeddings(Embeddings):
    def embed_documents(self, texts):
        # Return a dummy embedding for setup purposes
        return [[0.1] * 1024 for _ in texts]
        
    def embed_query(self, text):
        return [0.1] * 1024

# Create LangChain PGVector tables without loading data
def create_pgvector_tables():
    print("Creating PGVector tables for LangChain...")
    conn_string = get_db_connection_string()
    embedding_length = 1024  # from config
    
    try:
        # Create an instance of PGVector and use the instance method to create tables
        embeddings = DummyEmbeddings()
        vector_store = PGVector(
            embeddings=embeddings,
            connection=conn_string,
            collection_name="bible_verses",
            embedding_length=embedding_length,
            use_jsonb=True
        )
        
        # Create the tables using instance methods
        vector_store.create_vector_extension()
        vector_store.create_tables_if_not_exists()
        
        print("PGVector tables created successfully")
        return True
    except Exception as e:
        print(f"Error creating PGVector tables: {e}")
        return False

if __name__ == "__main__":
    create_pgvector_tables()