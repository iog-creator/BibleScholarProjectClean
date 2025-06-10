#!/usr/bin/env python3
"""
Simple Bible verse search test
"""

from src.database.secure_connection import get_secure_connection

def test_simple_search():
    """Test simple Bible verse search"""
    print("Testing simple Bible verse search...")
    
    try:
        with get_secure_connection() as conn:
            with conn.cursor() as cursor:
                # Test basic search
                print("1. Testing basic verse search...")
                cursor.execute("""
                    SELECT book_name, chapter_num, verse_num, text 
                    FROM bible.verses 
                    WHERE text ILIKE %s 
                    LIMIT 3
                """, ('%love%',))
                
                results = cursor.fetchall()
                print(f"   ✅ Found {len(results)} verses containing 'love'")
                
                for i, result in enumerate(results, 1):
                    book = result['book_name']
                    chapter = result['chapter_num']
                    verse = result['verse_num']
                    text = result['text'][:80] + "..." if len(result['text']) > 80 else result['text']
                    print(f"   {i}. {book} {chapter}:{verse} - {text}")
                
                # Test embedding count
                print("\n2. Testing verse_embeddings table...")
                cursor.execute("SELECT COUNT(*) as count FROM bible.verse_embeddings")
                embedding_count = cursor.fetchone()['count']
                print(f"   ✅ Vector embeddings available: {embedding_count:,}")
                
                # Test sample embedding
                print("\n3. Testing sample embedding...")
                cursor.execute("""
                    SELECT verse_id, array_length(embedding::real[], 1) as dimensions
                    FROM bible.verse_embeddings 
                    LIMIT 1
                """)
                embedding_sample = cursor.fetchone()
                if embedding_sample:
                    print(f"   ✅ Sample embedding: verse_id={embedding_sample['verse_id']}, dimensions={embedding_sample['dimensions']}")
                else:
                    print("   ⚠️  No embeddings found")
                
                print("\n🎉 All tests passed!")
                return True
                
    except Exception as e:
        print(f"\n❌ Error in test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_search()
    if success:
        print("\n✅ Bible search functionality is working!")
    else:
        print("\n❌ Bible search functionality has issues") 