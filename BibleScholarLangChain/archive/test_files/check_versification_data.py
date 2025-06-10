import psycopg
from psycopg.rows import dict_row

def check_versification_data():
    """Check actual data in versification_mappings table"""
    try:
        conn = psycopg.connect(
            host="localhost",
            dbname="bible_db", 
            user="postgres",
            password="postgres",
            row_factory=dict_row
        )
        
        with conn.cursor() as cursor:
            # Check total count
            cursor.execute("SELECT COUNT(*) as count FROM bible.versification_mappings")
            count = cursor.fetchone()['count']
            print(f"✅ Total versification mappings: {count}")
            
            # Sample a few mappings
            cursor.execute("""
                SELECT source_book, source_chapter, source_verse, 
                       target_book, target_chapter, target_verse,
                       source_tradition, target_tradition 
                FROM bible.versification_mappings 
                LIMIT 5
            """)
            mappings = cursor.fetchall()
            print("\n📊 Sample mappings:")
            for mapping in mappings:
                print(f"  {mapping['source_book']} {mapping['source_chapter']}:{mapping['source_verse']} → {mapping['target_book']} {mapping['target_chapter']}:{mapping['target_verse']}")
            
            # Check what book names look like in verses vs mappings
            cursor.execute("SELECT DISTINCT book_name FROM bible.verses ORDER BY book_name LIMIT 10")
            verse_books = [row['book_name'] for row in cursor.fetchall()]
            print(f"\n📖 Sample verse book names: {verse_books}")
            
            cursor.execute("SELECT DISTINCT source_book FROM bible.versification_mappings ORDER BY source_book LIMIT 10")
            mapping_books = [row['source_book'] for row in cursor.fetchall()]
            print(f"🗺️  Sample mapping book names: {mapping_books}")
            
            # Test join with actual verse data
            cursor.execute("""
                SELECT verse_id, book_name, chapter_num, verse_num 
                FROM bible.verses 
                WHERE text ILIKE '%love%'
                LIMIT 3
            """)
            love_verses = cursor.fetchall()
            print(f"\n💕 Sample love verses:")
            for verse in love_verses:
                print(f"  {verse['verse_id']}: {verse['book_name']} {verse['chapter_num']}:{verse['verse_num']}")
                
                # Try to find mapping for this specific verse
                cursor.execute("""
                    SELECT COUNT(*) as matches
                    FROM bible.versification_mappings vm
                    WHERE vm.source_book = %s 
                    AND vm.source_chapter = %s
                    AND vm.source_verse = %s
                """, (verse['book_name'], str(verse['chapter_num']), str(verse['verse_num'])))
                matches = cursor.fetchone()['matches']
                print(f"    Mappings for this verse: {matches}")
                
                if matches > 0:
                    cursor.execute("""
                        SELECT source_book, source_chapter, source_verse,
                               target_book, target_chapter, target_verse
                        FROM bible.versification_mappings vm
                        WHERE vm.source_book = %s 
                        AND vm.source_chapter = %s
                        AND vm.source_verse = %s
                        LIMIT 2
                    """, (verse['book_name'], str(verse['chapter_num']), str(verse['verse_num'])))
                    verse_mappings = cursor.fetchall()
                    for mapping in verse_mappings:
                        print(f"      → {mapping['target_book']} {mapping['target_chapter']}:{mapping['target_verse']}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_versification_data() 