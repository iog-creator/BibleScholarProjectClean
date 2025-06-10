#!/usr/bin/env python3
"""
Comprehensive system status test for BibleScholarLangChain project
Tests servers, LM Studio, and database connectivity
"""

import requests
import psycopg
import sys
import subprocess
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")

def print_status(component, status, details=""):
    """Print formatted status line"""
    status_icon = "✅" if status == "OK" else "❌" if status == "ERROR" else "⚠️"
    print(f"{status_icon} {component}: {status}")
    if details:
        print(f"   {details}")

def test_servers():
    """Test API and Web UI servers"""
    print_header("SERVER STATUS")
    
    # Test API Server
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_status("API Server (port 5000)", "RUNNING", f"Server: {data.get('server', 'Unknown')}")
        else:
            print_status("API Server (port 5000)", "ERROR", f"HTTP {response.status_code}")
    except requests.exceptions.ConnectionError:
        print_status("API Server (port 5000)", "ERROR", "Connection refused - Server not running")
    except requests.exceptions.Timeout:
        print_status("API Server (port 5000)", "ERROR", "Timeout - Server not responding")
    except Exception as e:
        print_status("API Server (port 5000)", "ERROR", str(e))
    
    # Test Web UI Server
    try:
        response = requests.get('http://localhost:5002/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_status("Web UI Server (port 5002)", "RUNNING", f"Server: {data.get('server', 'Unknown')}")
            
            # Check if Web UI can reach API
            api_status = data.get('api_status', 'unknown')
            if api_status == 'accessible':
                print_status("Web UI → API Communication", "OK", "Web UI can reach API server")
            else:
                print_status("Web UI → API Communication", "WARNING", f"Status: {api_status}")
        else:
            print_status("Web UI Server (port 5002)", "ERROR", f"HTTP {response.status_code}")
    except requests.exceptions.ConnectionError:
        print_status("Web UI Server (port 5002)", "ERROR", "Connection refused - Server not running")
    except requests.exceptions.Timeout:
        print_status("Web UI Server (port 5002)", "ERROR", "Timeout - Server not responding")
    except Exception as e:
        print_status("Web UI Server (port 5002)", "ERROR", str(e))

def test_lm_studio():
    """Test LM Studio connectivity"""
    print_header("LM STUDIO STATUS")
    
    try:
        # Test models endpoint
        response = requests.get('http://localhost:1234/v1/models', timeout=10)
        if response.status_code == 200:
            data = response.json()
            model_count = len(data.get('data', []))
            print_status("LM Studio (port 1234)", "RUNNING", f"{model_count} models available")
            
            # List first few models
            if model_count > 0:
                models = data.get('data', [])[:3]  # Show first 3 models
                for model in models:
                    model_id = model.get('id', 'Unknown')
                    print(f"   - {model_id}")
                if model_count > 3:
                    print(f"   ... and {model_count - 3} more models")
        else:
            print_status("LM Studio (port 1234)", "ERROR", f"HTTP {response.status_code}")
    except requests.exceptions.ConnectionError:
        print_status("LM Studio (port 1234)", "ERROR", "Connection refused - LM Studio not running")
    except requests.exceptions.Timeout:
        print_status("LM Studio (port 1234)", "ERROR", "Timeout - LM Studio not responding")
    except Exception as e:
        print_status("LM Studio (port 1234)", "ERROR", str(e))

def test_database():
    """Test database connectivity"""
    print_header("DATABASE STATUS")
    
    conn_str = "postgresql://postgres:postgres@127.0.0.1:5432/bible_db"
    
    # Test PostgreSQL service
    try:
        result = subprocess.run(
            ['sc', 'query', 'postgresql-x64-14'], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        
        if "RUNNING" in result.stdout:
            print_status("PostgreSQL Service", "RUNNING", "Service is active")
        elif "STOPPED" in result.stdout:
            print_status("PostgreSQL Service", "ERROR", "Service is stopped - needs to be started")
            return False
        else:
            print_status("PostgreSQL Service", "WARNING", "Service status unclear")
    except Exception as e:
        print_status("PostgreSQL Service", "WARNING", f"Could not check service: {e}")
    
    # Test database connection
    try:
        conn = psycopg.connect(
            conn_str, 
            connect_timeout=10,
            options="-c statement_timeout=10000"
        )
        
        print_status("Database Connection", "OK", "Successfully connected to bible_db")
        
        # Test basic query
        with conn.cursor() as cursor:
            cursor.execute("SELECT version()")
            result = cursor.fetchone()
            version = result[0].split(' ')[1] if result else "Unknown"
            print_status("PostgreSQL Version", "OK", f"Version {version}")
            
        # Test database name
        with conn.cursor() as cursor:
            cursor.execute("SELECT current_database()")
            db_name = cursor.fetchone()[0]
            print_status("Database Name", "OK", f"Connected to: {db_name}")
            
        # Test bible schema
        with conn.cursor() as cursor:
            cursor.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'bible'")
            schema_result = cursor.fetchone()
            if schema_result:
                print_status("Bible Schema", "OK", "Schema exists")
            else:
                print_status("Bible Schema", "WARNING", "Schema does not exist")
                
        # Test tables
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'bible' 
                ORDER BY table_name
            """)
            tables = cursor.fetchall()
            if tables:
                table_names = [table[0] for table in tables]
                print_status("Bible Tables", "OK", f"Found {len(tables)} tables: {', '.join(table_names)}")
                
                # Test verse count if verses table exists
                if 'verses' in table_names:
                    cursor.execute("SELECT COUNT(*) FROM bible.verses")
                    verse_count = cursor.fetchone()[0]
                    print_status("Bible Verses", "OK", f"{verse_count:,} verses in database")
                
                # Test embeddings if table exists
                if 'verse_embeddings' in table_names:
                    cursor.execute("SELECT COUNT(*) FROM bible.verse_embeddings")
                    embedding_count = cursor.fetchone()[0]
                    print_status("Vector Embeddings", "OK", f"{embedding_count:,} embeddings in database")
            else:
                print_status("Bible Tables", "WARNING", "No tables found in bible schema")
        
        conn.close()
        return True
        
    except psycopg.OperationalError as e:
        error_msg = str(e)
        if "could not connect to server" in error_msg:
            print_status("Database Connection", "ERROR", "Cannot connect - PostgreSQL server not running")
        elif "database \"bible_db\" does not exist" in error_msg:
            print_status("Database Connection", "ERROR", "Database 'bible_db' does not exist")
        elif "authentication failed" in error_msg:
            print_status("Database Connection", "ERROR", "Authentication failed - check credentials")
        elif "timeout expired" in error_msg:
            print_status("Database Connection", "ERROR", "Connection timeout - PostgreSQL may not be running")
        else:
            print_status("Database Connection", "ERROR", error_msg)
        return False
        
    except Exception as e:
        print_status("Database Connection", "ERROR", f"Unexpected error: {e}")
        return False

def test_system_integration():
    """Test system integration and overall health"""
    print_header("SYSTEM INTEGRATION")
    
    # Test if all components can work together
    try:
        # Test Web UI health endpoint which checks multiple components
        response = requests.get('http://localhost:5002/health', timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # Check API connectivity from Web UI perspective
            api_status = data.get('api_status', 'unknown')
            if api_status == 'accessible':
                print_status("API Integration", "OK", "Web UI can communicate with API")
            else:
                print_status("API Integration", "WARNING", f"API status: {api_status}")
            
            # Check LM Studio connectivity from Web UI perspective
            lm_status = data.get('lm_studio_status', 'unknown')
            if lm_status == 'connected':
                print_status("LM Studio Integration", "OK", "Web UI can communicate with LM Studio")
            else:
                print_status("LM Studio Integration", "WARNING", f"LM Studio status: {lm_status}")
                
        else:
            print_status("System Integration", "ERROR", "Cannot reach Web UI health endpoint")
            
    except Exception as e:
        print_status("System Integration", "ERROR", f"Integration test failed: {e}")

def generate_summary():
    """Generate overall system status summary"""
    print_header("SYSTEM STATUS SUMMARY")
    
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Environment: BSPclean virtual environment")
    print(f"Project: BibleScholarLangChain")
    
    print("\nQuick Actions:")
    print("• Start servers: .\\start_servers.bat")
    print("• Test database: python test_db_connection.py")
    print("• Full system test: python test_full_system_status.py")
    print("• Web UI: http://localhost:5002")
    print("• API docs: http://localhost:5000/health")
    
    print("\nTroubleshooting:")
    print("• Database issues: See database_setup_guide.md")
    print("• Server issues: Check logs/ directory")
    print("• LM Studio: Ensure LM Studio is running on port 1234")

if __name__ == "__main__":
    print("BibleScholarLangChain - Full System Status Check")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    test_servers()
    test_lm_studio()
    database_ok = test_database()
    test_system_integration()
    generate_summary()
    
    # Exit with appropriate code
    if not database_ok:
        print(f"\n❌ CRITICAL: Database connectivity failed!")
        print("💡 See database_setup_guide.md for troubleshooting steps")
        sys.exit(1)
    else:
        print(f"\n✅ System check completed successfully!")
        sys.exit(0) 