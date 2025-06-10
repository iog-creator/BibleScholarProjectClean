#!/usr/bin/env python3
"""
Simple database connection test with timeout handling
"""

import psycopg
import sys
import signal
from contextlib import contextmanager

def timeout_handler(signum, frame):
    raise TimeoutError("Database connection timed out")

@contextmanager
def timeout(seconds):
    """Context manager for timeout handling"""
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

def test_db_connection_simple():
    """Test database connection with timeout"""
    conn_str = "postgresql://postgres:postgres@localhost:5432/bible_db"
    
    print("Testing database connection...")
    print(f"Connection string: {conn_str}")
    
    try:
        # Test with 10 second timeout
        print("Attempting connection (10 second timeout)...")
        
        # For Windows, we can't use signal, so use psycopg's connect_timeout
        conn = psycopg.connect(
            conn_str, 
            connect_timeout=10,
            options="-c statement_timeout=10000"
        )
        
        print("✅ Connection successful!")
        
        # Test basic query
        with conn.cursor() as cursor:
            cursor.execute("SELECT version()")
            result = cursor.fetchone()
            print(f"✅ Database version: {result[0]}")
            
        # Test if bible_db exists
        with conn.cursor() as cursor:
            cursor.execute("SELECT current_database()")
            db_name = cursor.fetchone()[0]
            print(f"✅ Connected to database: {db_name}")
            
        # Test if bible schema exists
        with conn.cursor() as cursor:
            cursor.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'bible'")
            schema_result = cursor.fetchone()
            if schema_result:
                print("✅ Bible schema exists")
            else:
                print("⚠️  Bible schema does not exist")
                
        # Test if tables exist
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'bible' 
                ORDER BY table_name
            """)
            tables = cursor.fetchall()
            if tables:
                print(f"✅ Found {len(tables)} tables in bible schema:")
                for table in tables:
                    print(f"   - {table[0]}")
            else:
                print("⚠️  No tables found in bible schema")
        
        conn.close()
        return True
        
    except psycopg.OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        if "could not connect to server" in str(e):
            print("💡 Suggestion: Make sure PostgreSQL server is running")
        elif "database \"bible_db\" does not exist" in str(e):
            print("💡 Suggestion: Create the bible_db database first")
        elif "authentication failed" in str(e):
            print("💡 Suggestion: Check username/password credentials")
        return False
        
    except TimeoutError:
        print("❌ Connection timed out after 10 seconds")
        print("💡 Suggestion: Check if PostgreSQL server is running and accessible")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_postgres_service():
    """Test if PostgreSQL service is running (Windows)"""
    import subprocess
    
    try:
        print("\nChecking PostgreSQL service status...")
        result = subprocess.run(
            ['sc', 'query', 'postgresql-x64-14'], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        
        if "RUNNING" in result.stdout:
            print("✅ PostgreSQL service is running")
            return True
        elif "STOPPED" in result.stdout:
            print("❌ PostgreSQL service is stopped")
            print("💡 Suggestion: Start PostgreSQL service")
            return False
        else:
            print("⚠️  PostgreSQL service status unclear")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  Service check timed out")
        return False
    except FileNotFoundError:
        print("⚠️  'sc' command not found (not Windows?)")
        return False
    except Exception as e:
        print(f"⚠️  Error checking service: {e}")
        return False

if __name__ == "__main__":
    print("=== Database Connection Diagnostic ===")
    
    # Test PostgreSQL service
    service_running = test_postgres_service()
    
    # Test database connection
    connection_success = test_db_connection_simple()
    
    print("\n=== Summary ===")
    if service_running and connection_success:
        print("✅ Database is fully accessible")
    elif not service_running:
        print("❌ PostgreSQL service needs to be started")
    elif not connection_success:
        print("❌ Database connection issues detected")
    else:
        print("⚠️  Mixed results - check logs above") 