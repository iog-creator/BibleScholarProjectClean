import os
import requests
from langchain_postgres.vectorstores import PGVector
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
import psycopg
from psycopg.rows import dict_row
import sys
sys.path.append('C:\\Users\\mccoy\\Documents\\Projects\\Projects\\CursorMCPWorkspace')
from BibleScholarLangChain.scripts.db_config import get_config
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

def get_secure_connection():
    """Create a secure database connection using psycopg3"""
    config = get_config()
    try:
        connection_string = config['database']['connection_string']
        conn = psycopg.connect(connection_string, row_factory=dict_row)
        print(Fore.GREEN + "Database connection successful")
        return conn
    except Exception as e:
        print(Fore.RED + f"Connection error: {e}")
        raise

def load_bible_data():
    print(Fore.CYAN + "Checking PGVector store...")
    config = get_config()
    conn = get_secure_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'verse_embeddings')")
        exists = cursor.fetchone()['exists']
    if exists:
        print(Fore.GREEN + "Using existing bible.verse_embeddings")
        conn.close()
        return
    print(Fore.CYAN + "Loading Bible data into PGVector...")
    with conn.cursor() as cursor:
        cursor.execute("SELECT book_name, chapter_num, verse_num, verse_text, translation_source, verse_id FROM bible.verses WHERE translation_source IN ('KJV', 'ASV') LIMIT 100")
        verses = cursor.fetchall()
    conn.close()
    documents = [
        Document(
            page_content=verse['verse_text'],
            metadata={"book": verse['book_name'], "chapter": verse['chapter_num'], 
                      "verse": verse['verse_num'], "translation": verse['translation_source'], 
                      "verse_id": verse['verse_id']}
        )
        for verse in verses
    ]
    ids = [f"{verse['book_name']}_{verse['chapter_num']}_{verse['verse_num']}_{verse['translation_source']}" for verse in verses]
    embeddings = LMStudioEmbedding(config['api']['lm_studio_url'], config['vector_search']['embedding_model'])
    vector_store = PGVector(
        embeddings=embeddings,
        connection=config['database']['connection_string'],
        collection_name="verse_embeddings",
        use_jsonb=True,
        embedding_length=config['vector_search']['embedding_length']
    )
    vector_store.add_documents(documents, ids=ids)
    print(Fore.GREEN + f"Loaded {len(documents)} verses into PGVector")

if __name__ == "__main__":
    load_bible_data()