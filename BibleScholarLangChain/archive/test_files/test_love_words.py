#!/usr/bin/env python3
import psycopg
from psycopg.rows import dict_row

def test_love_words():
    conn = psycopg.connect('postgresql://postgres:postgres@127.0.0.1:5432/bible_db', row_factory=dict_row)
    with conn.cursor() as cursor:
        
        print("=== FINDING ACTUAL LOVE WORDS ===\n")
        
        # Find Greek words with love in gloss
        cursor.execute("SELECT COUNT(*) FROM bible.greek_nt_words WHERE gloss ILIKE '%love%'")
        greek_love_words = cursor.fetchone()['count']
        print(f"Greek words with 'love' in gloss: {greek_love_words}")
        
        # Find Hebrew words with love in gloss  
        cursor.execute("SELECT COUNT(*) FROM bible.hebrew_ot_words WHERE gloss ILIKE '%love%'")
        hebrew_love_words = cursor.fetchone()['count']
        print(f"Hebrew words with 'love' in gloss: {hebrew_love_words}")
        
        # Sample Greek love words
        cursor.execute("""
            SELECT gw.verse_id, gw.word_text, gw.strongs_id, gw.gloss, v.book_name, v.chapter_num, v.verse_num
            FROM bible.greek_nt_words gw
            JOIN bible.verses v ON gw.verse_id = v.verse_id  
            WHERE gw.gloss ILIKE '%love%'
            LIMIT 5
        """)
        greek_samples = cursor.fetchall()
        print(f"\nGreek love word samples: {len(greek_samples)}")
        for row in greek_samples:
            print(f"  {row['book_name']} {row['chapter_num']}:{row['verse_num']} - {row['word_text']} ({row['strongs_id']}) = {row['gloss']}")
            
        # Sample Hebrew love words
        cursor.execute("""
            SELECT hw.verse_id, hw.word_text, hw.strongs_id, hw.gloss, v.book_name, v.chapter_num, v.verse_num
            FROM bible.hebrew_ot_words hw
            JOIN bible.verses v ON hw.verse_id = v.verse_id
            WHERE hw.gloss ILIKE '%love%'
            LIMIT 5
        """)
        hebrew_samples = cursor.fetchall()
        print(f"\nHebrew love word samples: {len(hebrew_samples)}")
        for row in hebrew_samples:
            print(f"  {row['book_name']} {row['chapter_num']}:{row['verse_num']} - {row['word_text']} ({row['strongs_id']}) = {row['gloss']}")

if __name__ == "__main__":
    test_love_words() 