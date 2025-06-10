#!/usr/bin/env python3
"""
Test LM Studio integration and add database indexes
"""
import os
import requests
import psycopg
from psycopg.rows import dict_row
import json

def test_lm_studio():
    """Test LM Studio endpoints"""
    print("=== Testing LM Studio Integration ===")
    
    # Test models endpoint
    try:
        response = requests.get('http://localhost:1234/v1/models', timeout=10)
        if response.status_code == 200:
            models = response.json()
            print(f"✓ LM Studio models endpoint working - {len(models['data'])} models available")
            
            # Check for required models
            model_ids = [model['id'] for model in models['data']]
            if 'meta-llama-3.1-8b-instruct' in model_ids:
                print("✓ meta-llama-3.1-8b-instruct model available")
            if 'text-embedding-bge-m3' in model_ids:
                print("✓ text-embedding-bge-m3 model available")
        else:
            print(f"✗ LM Studio models endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"✗ LM Studio models test failed: {e}")
    
    # Test embeddings endpoint
    try:
        response = requests.post(
            'http://localhost:1234/v1/embeddings',
            json={"input": "test", "model": "text-embedding-bge-m3"},
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            embedding = data['data'][0]['embedding']
            print(f"✓ LM Studio embeddings endpoint working - {len(embedding)} dimensions")
        else:
            print(f"✗ LM Studio embeddings endpoint failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ LM Studio embeddings test failed: {e}")
    
    # Test chat completions endpoint
    try:
        response = requests.post(
            'http://localhost:1234/v1/chat/completions',
            json={
                "model": "meta-llama-3.1-8b-instruct",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            },
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            print(f"✓ LM Studio chat completions working - Response: {content[:50]}...")
        else:
            print(f"✗ LM Studio chat completions failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ LM Studio chat completions test failed: {e}")

def setup_database_indexes():
    """Add database indexes for search optimization"""
    print("\n=== Setting Up Database Indexes ===")
    
    try:
        conn = psycopg.connect('postgresql://postgres:postgres@localhost:5432/bible_db', row_factory=dict_row)
        with conn.cursor() as cursor:
            # Add full-text search index on verses.text
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_verses_text_gin ON bible.verses USING GIN (to_tsvector('english', text))")
            print("✓ Created full-text search index on verses.text")
            
            # Add regular index for ILIKE searches
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_verses_text_ilike ON bible.verses (text)")
            print("✓ Created ILIKE index on verses.text")
            
            # Add composite index for book/chapter/verse lookups
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_verses_reference ON bible.verses (book, chapter, verse)")
            print("✓ Created composite index on book/chapter/verse")
            
            conn.commit()
            print("✓ All database indexes created successfully")
            
            # Test verse count
            cursor.execute('SELECT COUNT(*) as count FROM bible.verses')
            verse_count = cursor.fetchone()['count']
            print(f"✓ Total verses in database: {verse_count}")
            
            # Test embeddings table
            cursor.execute('SELECT COUNT(*) as count FROM bible.verse_embeddings')
            embedding_count = cursor.fetchone()['count']
            print(f"✓ Total embeddings in database: {embedding_count}")
            
    except Exception as e:
        print(f"✗ Database operation failed: {e}")

def test_search_performance():
    """Test search performance with new indexes"""
    print("\n=== Testing Search Performance ===")
    
    try:
        conn = psycopg.connect('postgresql://postgres:postgres@localhost:5432/bible_db', row_factory=dict_row)
        with conn.cursor() as cursor:
            # Set timeout
            cursor.execute("SET statement_timeout = '30s'")
            
            # Test full-text search
            import time
            start_time = time.time()
            cursor.execute(
                "SELECT book, chapter, verse, text FROM bible.verses "
                "WHERE to_tsvector('english', text) @@ plainto_tsquery('english', %s) "
                "LIMIT 5",
                ("love",)
            )
            results = cursor.fetchall()
            search_time = time.time() - start_time
            print(f"✓ Full-text search for 'love': {len(results)} results in {search_time:.3f}s")
            
            # Test ILIKE search
            start_time = time.time()
            cursor.execute(
                "SELECT book, chapter, verse, text FROM bible.verses "
                "WHERE text ILIKE %s LIMIT 5",
                ("%love%",)
            )
            results = cursor.fetchall()
            search_time = time.time() - start_time
            print(f"✓ ILIKE search for 'love': {len(results)} results in {search_time:.3f}s")
            
    except Exception as e:
        print(f"✗ Search performance test failed: {e}")

if __name__ == "__main__":
    test_lm_studio()
    setup_database_indexes()
    test_search_performance()
    print("\n=== Test Complete ===") 