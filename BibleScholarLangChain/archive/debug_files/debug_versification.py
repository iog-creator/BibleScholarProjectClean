import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Use the same connection function as the API
import psycopg
from psycopg.rows import dict_row

def get_db_connection():
    """Get database connection"""
    return psycopg.connect(
        host="localhost",
        dbname="bible_db", 
        user="postgres",
        password="postgres",
        row_factory=dict_row
    )

def debug_versification():
    """Debug the versification mapping table"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                
                # Check if versification_mappings table has any data
                print("=== VERSIFICATION MAPPINGS TABLE ===")
                cursor.execute("SELECT COUNT(*) FROM bible.versification_mappings")
                count = cursor.fetchone()[0]
                print(f"Total versification mappings: {count}")
                
                if count > 0:
                    # Sample some mappings
                    cursor.execute("""
                        SELECT source_book, source_chapter, source_verse, 
                               target_book, target_chapter, target_verse,
                               source_tradition, target_tradition 
                        FROM bible.versification_mappings 
                        LIMIT 10
                    """)
                    mappings = cursor.fetchall()
                    print("\nSample mappings:")
                    for mapping in mappings:
                        print(f"  {mapping}")
                
                # Check verse format in verses table
                print("\n=== VERSES TABLE FORMAT ===")
                cursor.execute("""
                    SELECT verse_id, book_name, chapter_num, verse_num 
                    FROM bible.verses 
                    WHERE book_name IN ('Genesis', 'Matthew', '1 Corinthians')
                    LIMIT 5
                """)
                verses = cursor.fetchall()
                print("Sample verses:")
                for verse in verses:
                    print(f"  {verse}")
                
                # Check for specific love verse format
                print("\n=== LOVE VERSE EXAMPLES ===")
                cursor.execute("""
                    SELECT verse_id, book_name, chapter_num, verse_num, LEFT(text, 50) as text_sample
                    FROM bible.verses 
                    WHERE text ILIKE '%love%'
                    LIMIT 5
                """)
                love_verses = cursor.fetchall()
                print("Love verses format:")
                for verse in love_verses:
                    print(f"  {verse}")
                
                # Test the exact join condition
                print("\n=== TESTING JOIN CONDITION ===")
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM bible.versification_mappings vm
                    JOIN bible.verses v ON (
                        v.book_name = vm.source_book 
                        AND v.chapter_num::text = vm.source_chapter 
                        AND v.verse_num::text = vm.source_verse
                    )
                """)
                join_count = cursor.fetchone()[0]
                print(f"Successful joins between verses and versification_mappings: {join_count}")
                
                # Check book name variations
                print("\n=== BOOK NAME COMPARISON ===")
                cursor.execute("SELECT DISTINCT book_name FROM bible.verses ORDER BY book_name LIMIT 10")
                verse_books = [row[0] for row in cursor.fetchall()]
                print(f"Verse book names: {verse_books}")
                
                if count > 0:
                    cursor.execute("SELECT DISTINCT source_book FROM bible.versification_mappings ORDER BY source_book LIMIT 10")
                    mapping_books = [row[0] for row in cursor.fetchall()]
                    print(f"Mapping book names: {mapping_books}")
                
    except Exception as e:
        print(f"Error debugging versification: {e}")

if __name__ == "__main__":
    debug_versification() 