#!/usr/bin/env python3
"""
Verify psycopg3 compatibility with langchain-postgres and PGVector
"""
import os
import sys
import importlib.util
import subprocess

# Define paths
venv_path = r'C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace\BSPclean'
project_path = r'C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace\BibleScholarLangChain'

def verify_psycopg_version():
    """Verify psycopg version and make sure no psycopg2 is installed"""
    try:
        print("=== Checking psycopg installation ===")
        # Check installed packages
        result = subprocess.run([os.path.join(venv_path, 'Scripts', 'pip.exe'), 'freeze'], 
                               capture_output=True, text=True)
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
        
        if has_psycopg2:
            print("WARNING: psycopg2 is still installed, which may cause conflicts")
            print("Uninstalling psycopg2...")
            subprocess.run([os.path.join(venv_path, 'Scripts', 'pip.exe'), 'uninstall', '-y', 
                           'psycopg2', 'psycopg2-binary'], capture_output=True, text=True)
            print("Reinstalling psycopg3...")
            subprocess.run([os.path.join(venv_path, 'Scripts', 'pip.exe'), 'install', 
                           'psycopg==3.1.8'], capture_output=True, text=True)
        
        if not has_psycopg3:
            print("WARNING: psycopg3 is not installed")
            print("Installing psycopg3...")
            subprocess.run([os.path.join(venv_path, 'Scripts', 'pip.exe'), 'install', 
                           'psycopg==3.1.8'], capture_output=True, text=True)
        
        # Import psycopg and check version
        print("\n=== Attempting to import psycopg ===")
        try:
            import psycopg
            print(f"Successfully imported psycopg version: {psycopg.__version__}")
            
            # Try to import psycopg2 (should fail if correctly uninstalled)
            try:
                import psycopg2
                print("WARNING: psycopg2 is still importable")
            except ImportError:
                print("Good: psycopg2 is not importable")
        except ImportError as e:
            print(f"Error importing psycopg: {e}")
            return False
        
        return True
    except Exception as e:
        print(f"Error checking psycopg installation: {e}")
        return False

def verify_langchain_postgres():
    """Verify langchain-postgres is using psycopg3"""
    try:
        print("\n=== Checking langchain-postgres compatibility ===")
        # Try to import the necessary modules
        try:
            from langchain_postgres import PGVector
            print("Successfully imported PGVector from langchain-postgres")
        except ImportError as e:
            print(f"Error importing PGVector: {e}")
            print("Installing langchain-postgres...")
            subprocess.run([os.path.join(venv_path, 'Scripts', 'pip.exe'), 'install', 
                           'langchain-postgres==0.0.13'], capture_output=True, text=True)
            try:
                from langchain_postgres import PGVector
                print("Successfully installed and imported PGVector")
            except ImportError as e:
                print(f"Still can't import PGVector after install: {e}")
                return False
        
        # Check if PGVector is using psycopg
        import inspect
        from langchain_postgres.vectorstores import PGVector
        
        source_code = inspect.getsource(PGVector)
        if 'psycopg2' in source_code:
            print("WARNING: PGVector source code contains references to psycopg2")
        else:
            print("Good: PGVector source code doesn't reference psycopg2")
        
        if 'psycopg' in source_code:
            print("Good: PGVector source code references psycopg")
        else:
            print("WARNING: PGVector source code doesn't reference psycopg")
        
        # Verify PGVector can create a connection
        print("\n=== Testing PGVector connection ===")
        from langchain_core.embeddings import Embeddings
        
        class DummyEmbeddings(Embeddings):
            def embed_documents(self, texts):
                return [[0.1] * 1024 for _ in texts]
                
            def embed_query(self, text):
                return [0.1] * 1024
        
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
            print(f"Successfully accessed collection: {collection}")
            return True
        except Exception as e:
            print(f"Error accessing PGVector collection: {e}")
            return False
        
    except Exception as e:
        print(f"Error checking langchain-postgres: {e}")
        return False

if __name__ == "__main__":
    print("=== PSYCOPG3 COMPATIBILITY VERIFICATION ===")
    print(f"Using Python: {sys.executable}")
    
    psycopg_ok = verify_psycopg_version()
    langchain_ok = verify_langchain_postgres()
    
    print("\n=== VERIFICATION SUMMARY ===")
    print(f"Psycopg3 installation: {'OK' if psycopg_ok else 'FAILED'}")
    print(f"LangChain-Postgres compatibility: {'OK' if langchain_ok else 'FAILED'}")
    
    if psycopg_ok and langchain_ok:
        print("\nVERIFICATION PASSED: The environment is correctly set up to use psycopg3 with LangChain")
        sys.exit(0)
    else:
        print("\nVERIFICATION FAILED: There are issues with the psycopg3 setup")
        sys.exit(1) 