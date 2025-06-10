#!/usr/bin/env python3
"""
Test Bible verse search functionality
"""

from src.database.secure_connection import get_secure_connection

def test_bible_search():
    """Test basic Bible verse search"""
    print("Testing Bible verse search...")
    
    try:
        with get_secure_connection() as conn:
            with conn.cursor() as cursor:
                # Test basic search
                cursor.execute("""
                    SELECT book_name, chapter_num, verse_num, text 
                    FROM bible.verses 
                    WHERE text ILIKE %s 
                    LIMIT 5
                """, ('%love%',))
                
                results = cursor.fetchall()
                print(f"✅ Found {len(results)} verses containing 'love':")
                
                for result in results:
                    book = result['book_name']
                    chapter = result['chapter_num']
                    verse = result['verse_num']
                    text = result['text'][:100] + "..." if len(result['text']) > 100 else result['text']
                    print(f"   {book} {chapter}:{verse} - {text}")
                
                # Test embedding count
                cursor.execute("SELECT COUNT(*) as count FROM bible.verse_embeddings")
                embedding_count = cursor.fetchone()['count']
                print(f"\n✅ Vector embeddings available: {embedding_count:,}")
                
                # Test a sample embedding from verse_embeddings table
                cursor.execute("""
                    SELECT verse_id, cardinality(embedding) as dimensions
                    FROM bible.verse_embeddings 
                    LIMIT 1
                """)
                embedding_sample = cursor.fetchone()
                if embedding_sample:
                    print(f"✅ Sample embedding: verse_id={embedding_sample['verse_id']}, dimensions={embedding_sample['dimensions']}")
                
                # Test verses table embedding column
                cursor.execute("""
                    SELECT COUNT(*) as count 
                    FROM bible.verses 
                    WHERE embedding IS NOT NULL
                """)
                verses_with_embeddings = cursor.fetchone()['count']
                print(f"✅ Verses with embeddings in verses table: {verses_with_embeddings:,}")
                
                return True
                
    except Exception as e:
        print(f"❌ Bible search test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_bible_search()
    if success:
        print("\n🎉 Bible search functionality is working!")
    else:
        print("\n❌ Bible search functionality has issues") 