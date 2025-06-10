#!/usr/bin/env python3
"""
Simple Database Connection Test for BibleScholarLangChain

This test verifies that the database connection works correctly
with the secure_connection module.
"""

import sys
import os
from colorama import Fore, init

init(autoreset=True)

print(f"{Fore.CYAN}🔌 Testing Database Connection...")

# Add project root to path
sys.path.append('C:\\Users\\mccoy\\Documents\\Projects\\Projects\\CursorMCPWorkspace')

try:
    from BibleScholarLangChain.src.database.secure_connection import get_secure_connection
    print(f"{Fore.GREEN}✅ secure_connection imported successfully")
    
    # Test the context manager
    with get_secure_connection() as conn:
        print(f"{Fore.GREEN}✅ Connection established")
        print(f"{Fore.BLUE}Connection type: {type(conn)}")
        
        with conn.cursor() as cursor:
            print(f"{Fore.GREEN}✅ Cursor created")
            print(f"{Fore.BLUE}Cursor type: {type(cursor)}")
            
            # Simple test query
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            print(f"{Fore.GREEN}✅ Test query successful: {result}")
            
            # Count verses
            cursor.execute("SELECT COUNT(*) as count FROM bible.verses")
            verse_count = cursor.fetchone()
            print(f"{Fore.GREEN}✅ Verse count: {verse_count['count']}")
            
            # Count embeddings  
            cursor.execute("SELECT COUNT(*) as count FROM bible.verse_embeddings")
            embedding_count = cursor.fetchone()
            print(f"{Fore.GREEN}✅ Embedding count: {embedding_count['count']}")
    
    print(f"{Fore.GREEN}✅ Connection closed properly")
    
except Exception as e:
    print(f"{Fore.RED}❌ Database connection test failed: {e}")
    import traceback
    traceback.print_exc()

print(f"\n{Fore.CYAN}🎯 Database Connection Test Complete") 