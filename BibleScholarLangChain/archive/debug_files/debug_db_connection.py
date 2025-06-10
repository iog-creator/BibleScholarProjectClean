#!/usr/bin/env python3
"""
Detailed database connection debugging
"""

import psycopg
import sys

def test_connection_variations():
    """Test different connection string variations"""
    
    connection_strings = [
        "postgresql://postgres:postgres@localhost:5432/bible_db",
        "postgresql://postgres:postgres@127.0.0.1:5432/bible_db", 
        "postgresql://postgres:postgres@localhost:5432/postgres",
        "postgresql://postgres:postgres@127.0.0.1:5432/postgres",
        "postgresql://postgres@localhost:5432/bible_db",
        "postgresql://postgres@127.0.0.1:5432/bible_db",
    ]
    
    for i, conn_str in enumerate(connection_strings, 1):
        print(f"\n{i}. Testing: {conn_str}")
        try:
            conn = psycopg.connect(conn_str, connect_timeout=5)
            print("   ✅ CONNECTION SUCCESSFUL!")
            
            # Test basic query
            with conn.cursor() as cursor:
                cursor.execute("SELECT current_database(), current_user, version()")
                result = cursor.fetchone()
                print(f"   Database: {result[0]}")
                print(f"   User: {result[1]}")
                print(f"   Version: {result[2].split()[1]}")
                
            # List databases
            with conn.cursor() as cursor:
                cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false")
                databases = cursor.fetchall()
                db_names = [db[0] for db in databases]
                print(f"   Available databases: {', '.join(db_names)}")
                
            conn.close()
            return conn_str  # Return the working connection string
            
        except psycopg.OperationalError as e:
            error_msg = str(e)
            if "database" in error_msg and "does not exist" in error_msg:
                print(f"   ❌ Database doesn't exist: {error_msg}")
            elif "authentication failed" in error_msg:
                print(f"   ❌ Authentication failed: {error_msg}")
            elif "could not connect" in error_msg:
                print(f"   ❌ Connection failed: {error_msg}")
            elif "timeout" in error_msg:
                print(f"   ❌ Timeout: {error_msg}")
            else:
                print(f"   ❌ Error: {error_msg}")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
    
    return None

def test_database_creation():
    """Test creating the bible_db database if it doesn't exist"""
    print(f"\n{'='*50}")
    print("TESTING DATABASE CREATION")
    print(f"{'='*50}")
    
    # First connect to default postgres database
    conn_str = "postgresql://postgres:postgres@127.0.0.1:5432/postgres"
    
    try:
        conn = psycopg.connect(conn_str, connect_timeout=5)
        print("✅ Connected to default postgres database")
        
        # Check if bible_db exists
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'bible_db'")
            exists = cursor.fetchone()
            
            if exists:
                print("✅ bible_db database already exists")
            else:
                print("⚠️  bible_db database does not exist")
                print("   Creating bible_db database...")
                
                # Create database (must be outside transaction)
                conn.autocommit = True
                cursor.execute("CREATE DATABASE bible_db")
                print("✅ bible_db database created successfully")
                
        conn.close()
        
        # Now test connection to bible_db
        bible_conn_str = "postgresql://postgres:postgres@127.0.0.1:5432/bible_db"
        bible_conn = psycopg.connect(bible_conn_str, connect_timeout=5)
        print("✅ Successfully connected to bible_db")
        
        # Check for bible schema
        with bible_conn.cursor() as cursor:
            cursor.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'bible'")
            schema_exists = cursor.fetchone()
            
            if schema_exists:
                print("✅ bible schema exists")
            else:
                print("⚠️  bible schema does not exist")
                print("   Creating bible schema...")
                cursor.execute("CREATE SCHEMA bible")
                bible_conn.commit()
                print("✅ bible schema created successfully")
                
        # Check for pgvector extension
        with bible_conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
            vector_exists = cursor.fetchone()
            
            if vector_exists:
                print("✅ pgvector extension is installed")
            else:
                print("⚠️  pgvector extension not installed")
                print("   Installing pgvector extension...")
                try:
                    cursor.execute("CREATE EXTENSION vector")
                    bible_conn.commit()
                    print("✅ pgvector extension installed successfully")
                except Exception as e:
                    print(f"❌ Failed to install pgvector: {e}")
                    print("   Note: pgvector extension may need to be installed separately")
        
        bible_conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database creation failed: {e}")
        return False

def main():
    print("DATABASE CONNECTION DEBUGGING")
    print(f"{'='*50}")
    
    # Test various connection strings
    working_conn_str = test_connection_variations()
    
    if working_conn_str:
        print(f"\n✅ WORKING CONNECTION STRING: {working_conn_str}")
    else:
        print(f"\n❌ NO WORKING CONNECTION FOUND")
        print("Attempting database creation...")
        
        if test_database_creation():
            print("\n✅ Database setup completed. Retesting connections...")
            working_conn_str = test_connection_variations()
            
            if working_conn_str:
                print(f"\n✅ FINAL WORKING CONNECTION: {working_conn_str}")
            else:
                print(f"\n❌ Still no working connection after database creation")
        else:
            print(f"\n❌ Database creation failed")
    
    print(f"\n{'='*50}")
    print("DEBUGGING COMPLETE")
    print(f"{'='*50}")

if __name__ == "__main__":
    main() 