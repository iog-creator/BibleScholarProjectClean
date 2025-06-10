#!/usr/bin/env python3
"""Debug the JOIN between bible.verses and Strong's word tables"""

import psycopg
from psycopg.rows import dict_row

def get_connection():
    return psycopg.connect(
        "postgresql://postgres:postgres@127.0.0.1:5432/bible_db",
        row_factory=dict_row
    )

def debug_strongs_joins():
    print("=== DEBUGGING STRONG'S JOINS ===\n")
    
    with get_connection() as conn:
        with conn.cursor() as cursor:
            
            # 1. Check table existence and counts
            print("1. TABLE COUNTS:")
            cursor.execute("SELECT COUNT(*) as count FROM bible.verses")
            verse_count = cursor.fetchone()['count']
            print(f"   bible.verses: {verse_count:,} rows")
            
            cursor.execute("SELECT COUNT(*) as count FROM bible.greek_nt_words")
            greek_words_count = cursor.fetchone()['count']
            print(f"   bible.greek_nt_words: {greek_words_count:,} rows")
            
            cursor.execute("SELECT COUNT(*) as count FROM bible.hebrew_ot_words")
            hebrew_words_count = cursor.fetchone()['count']
            print(f"   bible.hebrew_ot_words: {hebrew_words_count:,} rows")
            
            cursor.execute("SELECT COUNT(*) as count FROM bible.greek_entries")
            greek_entries_count = cursor.fetchone()['count']
            print(f"   bible.greek_entries: {greek_entries_count:,} rows")
            
            cursor.execute("SELECT COUNT(*) as count FROM bible.hebrew_entries")
            hebrew_entries_count = cursor.fetchone()['count']
            print(f"   bible.hebrew_entries: {hebrew_entries_count:,} rows")
            
            # 2. Check verse_id ranges
            print("\n2. VERSE_ID RANGES:")
            cursor.execute("SELECT MIN(verse_id) as min_id, MAX(verse_id) as max_id FROM bible.verses")
            verse_range = cursor.fetchone()
            print(f"   bible.verses verse_id range: {verse_range['min_id']} to {verse_range['max_id']}")
            
            cursor.execute("SELECT MIN(verse_id) as min_id, MAX(verse_id) as max_id FROM bible.greek_nt_words WHERE verse_id IS NOT NULL")
            greek_range = cursor.fetchone()
            print(f"   bible.greek_nt_words verse_id range: {greek_range['min_id']} to {greek_range['max_id']}")
            
            cursor.execute("SELECT MIN(verse_id) as min_id, MAX(verse_id) as max_id FROM bible.hebrew_ot_words WHERE verse_id IS NOT NULL")
            hebrew_range = cursor.fetchone()
            print(f"   bible.hebrew_ot_words verse_id range: {hebrew_range['min_id']} to {hebrew_range['max_id']}")
            
            # 3. Test specific love Strong's IDs
            print("\n3. LOVE STRONG'S ID TESTS:")
            
            # Check G0025 (agapao)
            cursor.execute("SELECT COUNT(*) as count FROM bible.greek_nt_words WHERE strongs_id = 'G0025'")
            g0025_count = cursor.fetchone()['count']
            print(f"   G0025 (agapao) in greek_nt_words: {g0025_count} rows")
            
            cursor.execute("SELECT COUNT(*) as count FROM bible.greek_entries WHERE strongs_id = 'G0025'")
            g0025_entries = cursor.fetchone()['count']
            print(f"   G0025 (agapao) in greek_entries: {g0025_entries} rows")
            
            # Check H0157 (ahab)
            cursor.execute("SELECT COUNT(*) as count FROM bible.hebrew_ot_words WHERE strongs_id = 'H0157'")
            h0157_count = cursor.fetchone()['count']
            print(f"   H0157 (ahab) in hebrew_ot_words: {h0157_count} rows")
            
            cursor.execute("SELECT COUNT(*) as count FROM bible.hebrew_entries WHERE strongs_id = 'H0157'")
            h0157_entries = cursor.fetchone()['count']
            print(f"   H0157 (ahab) in hebrew_entries: {h0157_entries} rows")
            
            # 4. Test the EXACT JOIN we're using in the API
            print("\n4. TESTING API JOIN QUERY:")
            cursor.execute("""
                SELECT DISTINCT
                    gw.verse_id, gw.word_text, gw.strongs_id, gw.transliteration, gw.gloss,
                    ge.lemma, ge.definition, ge.usage, 'Greek' as language,
                    v.book_name, v.chapter_num, v.verse_num, v.text, v.translation_source
                FROM bible.greek_nt_words gw
                JOIN bible.greek_entries ge ON gw.strongs_id = ge.strongs_id
                JOIN bible.verses v ON gw.verse_id = v.verse_id
                WHERE gw.strongs_id IN ('G0025', 'G0026', 'G5368')
                LIMIT 5
            """)
            greek_join_results = cursor.fetchall()
            print(f"   Greek JOIN results: {len(greek_join_results)} rows")
            for row in greek_join_results:
                print(f"     {row['book_name']} {row['chapter_num']}:{row['verse_num']} - {row['word_text']} ({row['strongs_id']})")
            
            cursor.execute("""
                SELECT DISTINCT
                    hw.verse_id, hw.word_text, hw.strongs_id, hw.transliteration, hw.gloss,
                    he.lemma, he.definition, he.usage, 'Hebrew' as language,
                    v.book_name, v.chapter_num, v.verse_num, v.text, v.translation_source
                FROM bible.hebrew_ot_words hw
                JOIN bible.hebrew_entries he ON hw.strongs_id = he.strongs_id
                JOIN bible.verses v ON hw.verse_id = v.verse_id
                WHERE hw.strongs_id IN ('H0157', 'H0160', 'H2617')
                LIMIT 5
            """)
            hebrew_join_results = cursor.fetchall()
            print(f"   Hebrew JOIN results: {len(hebrew_join_results)} rows")
            for row in hebrew_join_results:
                print(f"     {row['book_name']} {row['chapter_num']}:{row['verse_num']} - {row['word_text']} ({row['strongs_id']})")
                
            # 5. Check individual join components
            print("\n5. INDIVIDUAL JOIN DIAGNOSTICS:")
            
            # Greek words exist?
            cursor.execute("SELECT * FROM bible.greek_nt_words WHERE strongs_id = 'G0025' LIMIT 1")
            greek_word_sample = cursor.fetchone()
            if greek_word_sample:
                print(f"   Greek word sample: verse_id={greek_word_sample['verse_id']}, word='{greek_word_sample['word_text']}'")
                
                # Does this verse exist?
                cursor.execute("SELECT * FROM bible.verses WHERE verse_id = %s", (greek_word_sample['verse_id'],))
                verse_exists = cursor.fetchone()
                print(f"   Corresponding verse exists: {verse_exists is not None}")
                if verse_exists:
                    print(f"     {verse_exists['book_name']} {verse_exists['chapter_num']}:{verse_exists['verse_num']}")
            else:
                print("   No Greek word samples found!")
            
            # Hebrew words exist?
            cursor.execute("SELECT * FROM bible.hebrew_ot_words WHERE strongs_id = 'H0157' LIMIT 1")
            hebrew_word_sample = cursor.fetchone()
            if hebrew_word_sample:
                print(f"   Hebrew word sample: verse_id={hebrew_word_sample['verse_id']}, word='{hebrew_word_sample['word_text']}'")
                
                # Does this verse exist?
                cursor.execute("SELECT * FROM bible.verses WHERE verse_id = %s", (hebrew_word_sample['verse_id'],))
                verse_exists = cursor.fetchone()
                print(f"   Corresponding verse exists: {verse_exists is not None}")
                if verse_exists:
                    print(f"     {verse_exists['book_name']} {verse_exists['chapter_num']}:{verse_exists['verse_num']}")
            else:
                print("   No Hebrew word samples found!")

if __name__ == "__main__":
    debug_strongs_joins() 