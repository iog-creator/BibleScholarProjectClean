#!/usr/bin/env python3
"""
Debug script for comprehensive search functionality
"""
import psycopg
from psycopg.rows import dict_row

def get_db_connection():
    """Get database connection"""
    conn_str = "postgresql://postgres:postgres@127.0.0.1:5432/bible_db"
    return psycopg.connect(conn_str, row_factory=dict_row)

def debug_love_search():
    """Debug love search across all components"""
    print("=== DEBUGGING COMPREHENSIVE LOVE SEARCH ===\n")
    
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            
            # 1. Test verse search for "love"
            print("1. VERSE SEARCH FOR 'LOVE':")
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM bible.verses 
                WHERE text ILIKE %s
            """, ('%love%',))
            count = cursor.fetchone()['count']
            print(f"   Total verses with 'love': {count:,}")
            
            if count > 0:
                cursor.execute("""
                    SELECT verse_id, book_name, chapter_num, verse_num, 
                           translation_source, LEFT(text, 80) as text_sample
                    FROM bible.verses 
                    WHERE text ILIKE %s 
                    ORDER BY book_name, chapter_num, verse_num
                    LIMIT 5
                """, ('%love%',))
                verses = cursor.fetchall()
                for v in verses:
                    print(f"   - {v['book_name']} {v['chapter_num']}:{v['verse_num']} ({v['translation_source']}) ID:{v['verse_id']}")
                    print(f"     {v['text_sample']}...")
                
                # Get verse IDs for further testing
                verse_ids = [v['verse_id'] for v in verses]
                print(f"   Using verse IDs: {verse_ids}")
                
                # 2. Test Strong's numbers for these verses
                print("\n2. STRONG'S NUMBERS FOR LOVE VERSES:")
                
                # Greek words
                cursor.execute("""
                    SELECT gw.verse_id, gw.word_text, gw.strongs_id, gw.gloss,
                           ge.lemma, ge.definition
                    FROM bible.greek_nt_words gw
                    LEFT JOIN bible.greek_entries ge ON gw.strongs_id = ge.strongs_id
                    WHERE gw.verse_id = ANY(%s) AND gw.strongs_id IS NOT NULL
                    LIMIT 10
                """, (verse_ids,))
                greek_words = cursor.fetchall()
                print(f"   Greek words found: {len(greek_words)}")
                for w in greek_words[:3]:
                    print(f"   - {w['word_text']} ({w['strongs_id']}): {w['lemma']} - {w['definition'][:50] if w['definition'] else 'No definition'}...")
                
                # Hebrew words
                cursor.execute("""
                    SELECT hw.verse_id, hw.word_text, hw.strongs_id, hw.gloss,
                           he.lemma, he.definition
                    FROM bible.hebrew_ot_words hw
                    LEFT JOIN bible.hebrew_entries he ON hw.strongs_id = he.strongs_id
                    WHERE hw.verse_id = ANY(%s) AND hw.strongs_id IS NOT NULL
                    LIMIT 10
                """, (verse_ids,))
                hebrew_words = cursor.fetchall()
                print(f"   Hebrew words found: {len(hebrew_words)}")
                for w in hebrew_words[:3]:
                    print(f"   - {w['word_text']} ({w['strongs_id']}): {w['lemma']} - {w['definition'][:50] if w['definition'] else 'No definition'}...")
                
                # 3. Test morphology
                print("\n3. MORPHOLOGICAL ANALYSIS:")
                cursor.execute("""
                    SELECT gw.verse_id, gw.word_text, gw.grammar_code, gmc.description
                    FROM bible.greek_nt_words gw
                    LEFT JOIN bible.greek_morphology_codes gmc ON gw.grammar_code = gmc.code
                    WHERE gw.verse_id = ANY(%s) AND gw.grammar_code IS NOT NULL
                    LIMIT 5
                """, (verse_ids,))
                greek_morph = cursor.fetchall()
                print(f"   Greek morphology entries: {len(greek_morph)}")
                for m in greek_morph[:2]:
                    print(f"   - {m['word_text']} ({m['grammar_code']}): {m['description']}")
                
            else:
                print("   No verses found with 'love' - checking database issue")
                
                # Check if verses table has data
                cursor.execute("SELECT COUNT(*) as count FROM bible.verses")
                total_verses = cursor.fetchone()['count']
                print(f"   Total verses in database: {total_verses:,}")
                
                # Check sample verse content
                cursor.execute("SELECT text FROM bible.verses LIMIT 3")
                samples = cursor.fetchall()
                print("   Sample verse texts:")
                for i, s in enumerate(samples):
                    print(f"   {i+1}. {s['text'][:100]}...")
            
            # 4. Test specific Strong's numbers for love
            print("\n4. SPECIFIC STRONG'S NUMBERS FOR LOVE:")
            
            # Greek agape (G26)
            cursor.execute("""
                SELECT strongs_id, lemma, definition
                FROM bible.greek_entries 
                WHERE strongs_id IN ('G0026', 'G0025', 'G5368')
                OR lemma ILIKE '%agape%' OR lemma ILIKE '%phileo%'
            """)
            love_strongs = cursor.fetchall()
            print(f"   Love-related Greek Strong's: {len(love_strongs)}")
            for s in love_strongs:
                print(f"   - {s['strongs_id']}: {s['lemma']} - {s['definition'][:100] if s['definition'] else 'No definition'}...")
            
            # Hebrew ahab (H157)
            cursor.execute("""
                SELECT strongs_id, lemma, definition
                FROM bible.hebrew_entries 
                WHERE strongs_id IN ('H0157', 'H0160', 'H2617')
                OR lemma ILIKE '%ahab%' OR lemma ILIKE '%chesed%'
            """)
            hebrew_love = cursor.fetchall()
            print(f"   Love-related Hebrew Strong's: {len(hebrew_love)}")
            for s in hebrew_love:
                print(f"   - {s['strongs_id']}: {s['lemma']} - {s['definition'][:100] if s['definition'] else 'No definition'}...")

def debug_api_search():
    """Debug the API search method"""
    print("\n=== DEBUGGING API SEARCH METHOD ===\n")
    
    # Test the same search method used by the API
    query = "What does love mean in Greek and Hebrew?"
    keywords = "love"
    
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            print(f"Testing API search for keywords: '{keywords}'")
            
            cursor.execute("""
                SELECT DISTINCT v.verse_id, v.book_name, v.chapter_num, v.verse_num, 
                       v.text, v.translation_source
                FROM bible.verses v
                WHERE v.text ILIKE %s
                ORDER BY v.book_name, v.chapter_num, v.verse_num, v.translation_source
                LIMIT 15
            """, (f'%{keywords}%',))
            
            results = cursor.fetchall()
            print(f"API method found: {len(results)} verses")
            
            for i, v in enumerate(results[:3]):
                print(f"{i+1}. {v['book_name']} {v['chapter_num']}:{v['verse_num']} ({v['translation_source']})")
                print(f"   {v['text'][:100]}...")

if __name__ == "__main__":
    debug_love_search()
    debug_api_search() 