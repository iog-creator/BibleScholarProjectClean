#!/usr/bin/env python3
"""
Test LangChain Integration for BibleScholarLangChain

This test file verifies that the LangChain integration works correctly
by testing imports and basic functionality.
"""

import sys
import os
from colorama import Fore, init

init(autoreset=True)

print(f"{Fore.CYAN}🧪 Testing LangChain Integration...")

# Test 1: Basic imports
print(f"\n{Fore.YELLOW}Test 1: Testing basic imports...")
try:
    import psycopg
    from psycopg.rows import dict_row
    print(f"{Fore.GREEN}✅ psycopg imports successful")
except Exception as e:
    print(f"{Fore.RED}❌ psycopg import failed: {e}")

# Test 2: LangChain imports
print(f"\n{Fore.YELLOW}Test 2: Testing LangChain imports...")
try:
    from langchain_postgres import PGVector
    from langchain_core.embeddings import Embeddings
    from langchain_core.documents import Document
    print(f"{Fore.GREEN}✅ LangChain packages imported successfully")
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"{Fore.RED}❌ LangChain import failed: {e}")
    LANGCHAIN_AVAILABLE = False

# Test 3: Database connection
print(f"\n{Fore.YELLOW}Test 3: Testing database connection...")
try:
    # Add project root to path
    sys.path.append('C:\\Users\\mccoy\\Documents\\Projects\\Projects\\CursorMCPWorkspace')
    
    # Try multiple import paths
    try:
        from BibleScholarLangChain.src.database.secure_connection import get_secure_connection
        print(f"{Fore.GREEN}✅ secure_connection imported (full path)")
    except ImportError:
        try:
            from src.database.secure_connection import get_secure_connection  
            print(f"{Fore.GREEN}✅ secure_connection imported (relative path)")
        except ImportError as e:
            print(f"{Fore.RED}❌ secure_connection import failed: {e}")
            raise
    
    # Test connection
    conn = get_secure_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
    conn.close()
    print(f"{Fore.GREEN}✅ Database connection successful")
    
except Exception as e:
    print(f"{Fore.RED}❌ Database connection failed: {e}")

# Test 4: LangChain integration module
print(f"\n{Fore.YELLOW}Test 4: Testing LangChain integration module...")
try:
    # Try multiple import paths
    try:
        from BibleScholarLangChain.src.database.langchain_integration import BibleLangChainStore
        print(f"{Fore.GREEN}✅ LangChain integration imported (full path)")
    except ImportError:
        try:
            from src.database.langchain_integration import BibleLangChainStore
            print(f"{Fore.GREEN}✅ LangChain integration imported (relative path)")
        except ImportError as e:
            print(f"{Fore.RED}❌ LangChain integration import failed: {e}")
            raise
    
    # Test initialization
    if LANGCHAIN_AVAILABLE:
        try:
            store = BibleLangChainStore()
            print(f"{Fore.GREEN}✅ BibleLangChainStore initialized successfully")
            
            # Test status
            status = store.get_store_status()
            print(f"{Fore.GREEN}✅ Store status retrieved: {len(status)} keys")
            
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ Store initialization issue: {e}")
    else:
        print(f"{Fore.YELLOW}⚠️ Skipping store test - LangChain not available")
        
except Exception as e:
    print(f"{Fore.RED}❌ LangChain integration test failed: {e}")

# Test 5: Comprehensive search API
print(f"\n{Fore.YELLOW}Test 5: Testing comprehensive search API imports...")
try:
    # Try multiple import paths
    try:
        from BibleScholarLangChain.src.api.comprehensive_search import comprehensive_search_api
        print(f"{Fore.GREEN}✅ Comprehensive search API imported (full path)")
    except ImportError:
        try:
            from src.api.comprehensive_search import comprehensive_search_api
            print(f"{Fore.GREEN}✅ Comprehensive search API imported (relative path)")
        except ImportError as e:
            print(f"{Fore.RED}❌ Comprehensive search API import failed: {e}")
            raise
    
    print(f"{Fore.GREEN}✅ API blueprint created successfully")
    
except Exception as e:
    print(f"{Fore.RED}❌ Comprehensive search API test failed: {e}")

print(f"\n{Fore.CYAN}🎯 Test Summary:")
print(f"{Fore.GREEN}✅ Tests completed")
print(f"{Fore.BLUE}ℹ️ LangChain Available: {LANGCHAIN_AVAILABLE}")
print(f"{Fore.BLUE}ℹ️ Working Directory: {os.getcwd()}")
print(f"{Fore.BLUE}ℹ️ Python Path: {sys.path[:3]}...") 