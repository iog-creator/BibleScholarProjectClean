#!/usr/bin/env python3
"""
Test vector/semantic search functionality
"""

from src.database.secure_connection import get_secure_connection

def test_vector_search():
    """Test vector similarity search"""
    print("Testing vector similarity search...")
    
    try:
        with get_secure_connection() as conn:
            with conn.cursor() as cursor:
                # Test vector similarity search
                print("1. Testing vector similarity search...")
                
                # Get a sample embedding to search with
                cursor.execute("""
                    SELECT embedding 
                    FROM bible.verse_embeddings 
                    WHERE verse_id = (
                        SELECT verse_id 
                        FROM bible.verses 
                        WHERE text ILIKE '%love%' 
                        LIMIT 1
                    )
                    LIMIT 1
                """)
                
                sample_embedding = cursor.fetchone()
                if not sample_embedding:
                    print("   ❌ No sample embedding found")
                    return False
                
                print("   ✅ Found sample embedding for similarity search")
                
                # Perform similarity search
                cursor.execute("""
                    SELECT 
                        ve.verse_id,
                        v.book_name,
                        v.chapter_num,
                        v.verse_num,
                        v.text,
                        ve.embedding <=> %s as distance
                    FROM bible.verse_embeddings ve
                    JOIN bible.verses v ON ve.verse_id = v.verse_id
                    ORDER BY ve.embedding <=> %s
                    LIMIT 5
                """, (sample_embedding['embedding'], sample_embedding['embedding']))
                
                results = cursor.fetchall()
                print(f"   ✅ Found {len(results)} similar verses:")
                
                for i, result in enumerate(results, 1):
                    book = result['book_name']
                    chapter = result['chapter_num']
                    verse = result['verse_num']
                    distance = result['distance']
                    text = result['text'][:80] + "..." if len(result['text']) > 80 else result['text']
                    print(f"   {i}. {book} {chapter}:{verse} (distance: {distance:.4f}) - {text}")
                
                # Test vector index exists
                print("\n2. Testing vector indexes...")
                cursor.execute("""
                    SELECT indexname, tablename 
                    FROM pg_indexes 
                    WHERE schemaname = 'bible' 
                    AND indexname LIKE '%vector%' OR indexname LIKE '%embedding%'
                """)
                
                indexes = cursor.fetchall()
                if indexes:
                    print(f"   ✅ Found {len(indexes)} vector indexes:")
                    for idx in indexes:
                        print(f"      - {idx['indexname']} on {idx['tablename']}")
                else:
                    print("   ⚠️  No vector indexes found")
                
                print("\n🎉 Vector search tests passed!")
                return True
                
    except Exception as e:
        print(f"\n❌ Error in vector search test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_vector_search()
    if success:
        print("\n✅ Vector search functionality is working!")
    else:
        print("\n❌ Vector search functionality has issues") 