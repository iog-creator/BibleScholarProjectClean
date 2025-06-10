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