#!/usr/bin/env python3
"""Check the format of Strong's IDs in Greek tables"""

import psycopg
from psycopg.rows import dict_row

def get_connection():
    return psycopg.connect(
        "postgresql://postgres:postgres@127.0.0.1:5432/bible_db",
        row_factory=dict_row
    )

def check_greek_formats():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            
            print("Greek word Strong's format samples:")
            cursor.execute("SELECT DISTINCT strongs_id FROM bible.greek_nt_words WHERE strongs_id IS NOT NULL ORDER BY strongs_id LIMIT 10")
            greek_words_format = [r['strongs_id'] for r in cursor.fetchall()]
            print(f"  greek_nt_words: {greek_words_format}")
            
            print("\nGreek entries format samples:")
            cursor.execute("SELECT DISTINCT strongs_id FROM bible.greek_entries WHERE strongs_id LIKE '%25%' ORDER BY strongs_id LIMIT 5")
            greek_entries_format = [r['strongs_id'] for r in cursor.fetchall()]
            print(f"  greek_entries: {greek_entries_format}")
            
            # Find love-related entries by checking text content
            print("\nSearching for love in Greek entries by content:")
            cursor.execute("SELECT strongs_id, lemma, definition FROM bible.greek_entries WHERE definition ILIKE '%love%' OR lemma ILIKE '%love%' OR lemma ILIKE '%agap%' OR lemma ILIKE '%phileo%' LIMIT 5")
            love_entries = cursor.fetchall()
            for entry in love_entries:
                print(f"  {entry['strongs_id']}: {entry['lemma']} - {entry['definition'][:50]}...")
            
            # Now check if any of these Strong's IDs exist in word table
            if love_entries:
                love_strongs = [entry['strongs_id'] for entry in love_entries]
                print(f"\nChecking if these IDs exist in greek_nt_words: {love_strongs}")
                cursor.execute("SELECT DISTINCT strongs_id FROM bible.greek_nt_words WHERE strongs_id = ANY(%s)", (love_strongs,))
                found_in_words = [r['strongs_id'] for r in cursor.fetchall()]
                print(f"  Found in greek_nt_words: {found_in_words}")
                
                # Try without G prefix
                love_strongs_no_g = [s.replace('G', '') for s in love_strongs if s.startswith('G')]
                print(f"\nTrying without 'G' prefix: {love_strongs_no_g}")
                cursor.execute("SELECT DISTINCT strongs_id FROM bible.greek_nt_words WHERE strongs_id = ANY(%s)", (love_strongs_no_g,))
                found_no_g = [r['strongs_id'] for r in cursor.fetchall()]
                print(f"  Found without G: {found_no_g}")
                
                # Try with leading zeros
                love_strongs_padded = [s.replace('G', '').zfill(4) for s in love_strongs if s.startswith('G')]
                print(f"\nTrying with padding: {love_strongs_padded}")
                cursor.execute("SELECT DISTINCT strongs_id FROM bible.greek_nt_words WHERE strongs_id = ANY(%s)", (love_strongs_padded,))
                found_padded = [r['strongs_id'] for r in cursor.fetchall()]
                print(f"  Found with padding: {found_padded}")

if __name__ == "__main__":
    check_greek_formats() 