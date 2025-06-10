#!/usr/bin/env python3
"""
Secure database connection module using psycopg3
"""
import psycopg
from psycopg.rows import dict_row
import sys
import os
import logging
from colorama import Fore, init
from contextlib import contextmanager
from typing import Generator

# Add the project root to path for imports
sys.path.append('C:\\Users\\mccoy\\Documents\\Projects\\Projects\\CursorMCPWorkspace')
from BibleScholarLangChain.scripts.db_config import get_database_url

init(autoreset=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.join('C:\\Users\\mccoy\\Documents\\Projects\\Projects\\CursorMCPWorkspace', 'database_connection.log'),
    filemode='a'
)
logger = logging.getLogger('database')

@contextmanager
def get_secure_connection() -> Generator[psycopg.Connection, None, None]:
    """
    Get a secure database connection with proper cleanup
    Uses psycopg3 with dict_row factory for dictionary-style access
    """
    conn = None
    try:
        conn_str = get_database_url()
        conn = psycopg.connect(conn_str, row_factory=dict_row)
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

def execute_query(query, params=None, fetch=True):
    """Execute a query and return results"""
    conn = get_secure_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or {})
            if fetch:
                return cursor.fetchall()
            conn.commit()
            return True
    except Exception as e:
        error_msg = f"Query error: {e}"
        print(Fore.RED + error_msg)
        logger.error(error_msg)
        raise
    finally:
        conn.close()

def test_connection():
    """Test the database connection"""
    try:
        with get_secure_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT version()")
                result = cursor.fetchone()
                print(f"Database connection successful: {result['version']}")
                
                # Test verse count
                cursor.execute("SELECT COUNT(*) as count FROM bible.verses")
                verse_count = cursor.fetchone()['count']
                print(f"Verses in database: {verse_count}")
                
                # Test embeddings count
                cursor.execute("SELECT COUNT(*) as count FROM bible.verse_embeddings")
                embedding_count = cursor.fetchone()['count']
                print(f"Embeddings in database: {embedding_count}")
                
                return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection() 