import os
import sys
import requests
import psycopg
from psycopg.rows import dict_row
from colorama import Fore, init

# Add project root to path for imports
sys.path.append('C:/Users/mccoy/Documents/Projects/Projects/CursorMCPWorkspace')
from BibleScholarLangChain.scripts.db_config import get_config

init(autoreset=True)

def check_file_exists(file_path):
    """Check if a file exists and print result"""
    exists = os.path.exists(file_path)
    if exists:
        print(Fore.GREEN + f"✓ File exists: {file_path}")
    else:
        print(Fore.RED + f"✗ File missing: {file_path}")
    return exists

def check_db_connection():
    """Test database connection"""
    try:
        # Get config from config.json
        config = get_config()
        connection_string = config['database']['connection_string']
        
        print(Fore.CYAN + "Testing database connection...")
        conn = psycopg.connect(connection_string, row_factory=dict_row)
        print(Fore.GREEN + "✓ Database connection successful")
        
        # Check if verse_embeddings table exists
        with conn.cursor() as cursor:
            cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'verse_embeddings')")
            exists = cursor.fetchone()['exists']
            if exists:
                print(Fore.GREEN + "✓ verse_embeddings table exists")
            else:
                print(Fore.RED + "✗ verse_embeddings table is missing")
                
            # Check sample verse
            cursor.execute("SELECT COUNT(*) FROM bible.verses WHERE book_name = 'John' AND chapter_num = 3 AND verse_num = 16")
            count = cursor.fetchone()['count']
            if count > 0:
                print(Fore.GREEN + f"✓ Found John 3:16 in database ({count} entries)")
            else:
                print(Fore.RED + "✗ John 3:16 not found in database")
                
        conn.close()
        return True
    except Exception as e:
        print(Fore.RED + f"✗ Database connection failed: {e}")
        return False

def check_api_endpoints():
    """Test API endpoints"""
    try:
        # Define endpoints to check
        endpoints = [
            ("Contextual Insights", "http://localhost:5000/api/contextual_insights/health", "GET"),
            ("Vector Search", "http://localhost:5000/api/vector_search/health", "GET"),
            ("Lexicon API", "http://localhost:5000/api/lexicon/health", "GET"),
            ("Search API", "http://localhost:5000/api/search/health", "GET"),
            ("Cross Language API", "http://localhost:5000/api/cross_language/health", "GET")
        ]
        
        # Try to connect to each endpoint
        results = []
        for name, url, method in endpoints:
            try:
                print(Fore.CYAN + f"Testing {name} endpoint: {url}")
                if method == "GET":
                    response = requests.get(url, timeout=2)
                else:
                    response = requests.post(url, timeout=2)
                
                if response.status_code == 200:
                    print(Fore.GREEN + f"✓ {name} endpoint is accessible ({response.status_code})")
                    results.append(True)
                else:
                    print(Fore.YELLOW + f"⚠ {name} endpoint returned: {response.status_code}")
                    results.append(False)
            except requests.exceptions.ConnectionError:
                print(Fore.RED + f"✗ {name} endpoint not accessible - connection error")
                results.append(False)
            except Exception as e:
                print(Fore.RED + f"✗ {name} endpoint error: {e}")
                results.append(False)
                
        return all(results)
    except Exception as e:
        print(Fore.RED + f"API test error: {e}")
        return False

def main():
    """Run all checks and tests"""
    print(Fore.CYAN + "=" * 50)
    print(Fore.CYAN + "Bible Scholar LangChain Setup Verification")
    print(Fore.CYAN + "=" * 50)
    
    # Check Python version
    print(Fore.CYAN + f"\nPython version: {sys.version}")
    
    # Check critical files
    print(Fore.CYAN + "\nChecking critical files...")
    required_files = [
        "C:\\Users\\mccoy\\Documents\\Projects\\Projects\\CursorMCPWorkspace\\BibleScholarLangChain\\config\\config.json",
        "C:\\Users\\mccoy\\Documents\\Projects\\Projects\\CursorMCPWorkspace\\BibleScholarLangChain\\.env",
        "C:\\Users\\mccoy\\Documents\\Projects\\Projects\\CursorMCPWorkspace\\BibleScholarLangChain\\scripts\\db_config.py",
        "C:\\Users\\mccoy\\Documents\\Projects\\Projects\\CursorMCPWorkspace\\BibleScholarLangChain\\src\\database\\secure_connection.py",
        "C:\\Users\\mccoy\\Documents\\Projects\\Projects\\CursorMCPWorkspace\\BibleScholarLangChain\\src\\api\\api_app.py",
        "C:\\Users\\mccoy\\Documents\\Projects\\Projects\\CursorMCPWorkspace\\BibleScholarLangChain\\src\\api\\vector_search_api.py",
        "C:\\Users\\mccoy\\Documents\\Projects\\Projects\\CursorMCPWorkspace\\BibleScholarLangChain\\src\\api\\lexicon_api.py",
        "C:\\Users\\mccoy\\Documents\\Projects\\Projects\\CursorMCPWorkspace\\BibleScholarLangChain\\src\\api\\search_api.py",
        "C:\\Users\\mccoy\\Documents\\Projects\\Projects\\CursorMCPWorkspace\\BibleScholarLangChain\\src\\api\\cross_language_api.py",
        "C:\\Users\\mccoy\\Documents\\Projects\\Projects\\CursorMCPWorkspace\\BibleScholarLangChain\\templates\\study_dashboard.html",
        "C:\\Users\\mccoy\\Documents\\Projects\\Projects\\CursorMCPWorkspace\\BibleScholarLangChain\\templates\\search.html",
        "C:\\Users\\mccoy\\Documents\\Projects\\Projects\\CursorMCPWorkspace\\BibleScholarLangChain\\static\\css\\dashboard.css",
        "C:\\Users\\mccoy\\Documents\\Projects\\Projects\\CursorMCPWorkspace\\BibleScholarLangChain\\static\\js\\dashboard.js",
        "C:\\Users\\mccoy\\Documents\\Projects\\Projects\\CursorMCPWorkspace\\BibleScholarLangChain\\web_app.py"
    ]
    
    files_exist = [check_file_exists(file) for file in required_files]
    
    # Check database connection
    print(Fore.CYAN + "\nTesting database connection...")
    db_ok = check_db_connection()
    
    # Check API endpoints
    print(Fore.CYAN + "\nTesting API endpoints...")
    api_ok = check_api_endpoints()
    
    # Summary
    print(Fore.CYAN + "\n" + "=" * 50)
    print(Fore.CYAN + "Setup Verification Summary")
    print(Fore.CYAN + "=" * 50)
    print(f"Files check: {Fore.GREEN if all(files_exist) else Fore.RED}{all(files_exist)}")
    print(f"Database connection: {Fore.GREEN if db_ok else Fore.RED}{db_ok}")
    print(f"API endpoints: {Fore.GREEN if api_ok else Fore.RED}{api_ok}")
    
    overall = all(files_exist) and db_ok and api_ok
    print(Fore.CYAN + "\nOverall status:")
    if overall:
        print(Fore.GREEN + "✓ Setup is complete and working correctly!")
    else:
        print(Fore.YELLOW + "⚠ Some issues were detected in the setup.")
        
    return overall

if __name__ == "__main__":
    main() 