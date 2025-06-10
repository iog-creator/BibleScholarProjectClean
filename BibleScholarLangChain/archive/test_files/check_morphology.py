#!/usr/bin/env python3
"""Check morphological data availability"""

import psycopg
from psycopg.rows import dict_row

def get_connection():
    return psycopg.connect(
        "postgresql://postgres:postgres@127.0.0.1:5432/bible_db",
        row_factory=dict_row
    )

def check_morphology():
    print("=== MORPHOLOGICAL DATA ANALYSIS ===\n")
    
    with get_connection() as conn:
        with conn.cursor() as cursor:
            
            # 1. Check morphology code tables
            print("1. MORPHOLOGY TABLES:")
            cursor.execute("SELECT COUNT(*) as count FROM bible.greek_morphology_codes")
            greek_morph_codes = cursor.fetchone()['count']
            print(f"   Greek morphology codes: {greek_morph_codes:,}")
            
            cursor.execute("SELECT COUNT(*) as count FROM bible.hebrew_morphology_codes")
            hebrew_morph_codes = cursor.fetchone()['count']
            print(f"   Hebrew morphology codes: {hebrew_morph_codes:,}")
            
            # 2. Check word tables with grammar codes
            print("\n2. WORDS WITH GRAMMAR CODES:")
            cursor.execute("SELECT COUNT(*) as count FROM bible.greek_nt_words WHERE grammar_code IS NOT NULL")
            greek_words_with_grammar = cursor.fetchone()['count']
            print(f"   Greek words with grammar codes: {greek_words_with_grammar:,}")
            
            cursor.execute("SELECT COUNT(*) as count FROM bible.hebrew_ot_words WHERE grammar_code IS NOT NULL")
            hebrew_words_with_grammar = cursor.fetchone()['count']
            print(f"   Hebrew words with grammar codes: {hebrew_words_with_grammar:,}")
            
            # 3. Sample love verse IDs from our previous query
            love_verse_ids = [70757, 130253, 70801, 130297, 161400]  # From 1Co 2:9, 4:14
            print(f"\n3. TESTING MORPHOLOGY FOR LOVE VERSES: {love_verse_ids}")
            
            # Test Greek morphology for these verses
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM bible.greek_nt_words gw
                WHERE gw.verse_id = ANY(%s) AND gw.grammar_code IS NOT NULL
            """, (love_verse_ids,))
            greek_morph_for_love = cursor.fetchone()['count']
            print(f"   Greek words with morphology in love verses: {greek_morph_for_love}")
            
            # Test Hebrew morphology
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM bible.hebrew_ot_words hw
                WHERE hw.verse_id = ANY(%s) AND hw.grammar_code IS NOT NULL
            """, (love_verse_ids,))
            hebrew_morph_for_love = cursor.fetchone()['count']
            print(f"   Hebrew words with morphology in love verses: {hebrew_morph_for_love}")
            
            # 4. Check actual JOIN query
            print("\n4. TESTING ACTUAL MORPHOLOGY JOIN:")
            cursor.execute("""
                SELECT 
                    gw.verse_id, gw.word_text, gw.grammar_code, gw.transliteration,
                    gmc.description, gmc.part_of_speech, 'Greek' as language
                FROM bible.greek_nt_words gw
                LEFT JOIN bible.greek_morphology_codes gmc ON gw.grammar_code = gmc.code
                WHERE gw.verse_id = ANY(%s) AND gw.grammar_code IS NOT NULL
                LIMIT 5
            """, (love_verse_ids,))
            greek_morph_results = cursor.fetchall()
            print(f"   Greek morphology JOIN results: {len(greek_morph_results)}")
            for row in greek_morph_results:
                print(f"     {row['word_text']} ({row['grammar_code']}) - {row['description']}")
                
            cursor.execute("""
                SELECT 
                    hw.verse_id, hw.word_text, hw.grammar_code, hw.transliteration,
                    hmc.description, hmc.part_of_speech, 'Hebrew' as language
                FROM bible.hebrew_ot_words hw
                LEFT JOIN bible.hebrew_morphology_codes hmc ON hw.grammar_code = hmc.code
                WHERE hw.verse_id = ANY(%s) AND hw.grammar_code IS NOT NULL
                LIMIT 5
            """, (love_verse_ids,))
            hebrew_morph_results = cursor.fetchall()
            print(f"   Hebrew morphology JOIN results: {len(hebrew_morph_results)}")
            for row in hebrew_morph_results:
                print(f"     {row['word_text']} ({row['grammar_code']}) - {row['description']}")
                
            # 5. Check what verses actually have Greek/Hebrew words
            print("\n5. VERSE-TO-WORDS MAPPING:")
            cursor.execute("""
                SELECT verse_id, COUNT(*) as word_count
                FROM bible.greek_nt_words 
                WHERE verse_id = ANY(%s)
                GROUP BY verse_id
            """, (love_verse_ids,))
            greek_verse_words = cursor.fetchall()
            print(f"   Greek words by verse: {dict((row['verse_id'], row['word_count']) for row in greek_verse_words)}")
            
            cursor.execute("""
                SELECT verse_id, COUNT(*) as word_count
                FROM bible.hebrew_ot_words 
                WHERE verse_id = ANY(%s)
                GROUP BY verse_id
            """, (love_verse_ids,))
            hebrew_verse_words = cursor.fetchall()
            print(f"   Hebrew words by verse: {dict((row['verse_id'], row['word_count']) for row in hebrew_verse_words)}")

if __name__ == "__main__":
    check_morphology() 