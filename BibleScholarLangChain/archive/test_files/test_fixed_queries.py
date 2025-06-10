#!/usr/bin/env python3
"""Test the fixed SQL queries directly"""

import psycopg
from psycopg.rows import dict_row

def get_connection():
    return psycopg.connect(
        "postgresql://postgres:postgres@127.0.0.1:5432/bible_db",
        row_factory=dict_row
    )

def test_fixed_queries():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            
            print("=== TESTING FIXED QUERIES ===\n")
            
            # Test Greek love query (fixed)
            print("1. Testing Greek love words query:")
            try:
                cursor.execute("""
                    SELECT DISTINCT
                        gw.verse_id, gw.word_text, gw.strongs_id, gw.transliteration, gw.gloss,
                        ge.lemma, ge.definition, ge.usage, 'Greek' as language,
                        v.book_name, v.chapter_num, v.verse_num, v.text, v.translation_source
                    FROM bible.greek_nt_words gw
                    JOIN bible.greek_entries ge ON gw.strongs_id = ge.strongs_id
                    JOIN bible.verses v ON gw.verse_id = v.verse_id
                    WHERE gw.strongs_id IN ('G0025', 'G0026', 'G5368')
                    OR ge.lemma ILIKE %s OR ge.lemma ILIKE %s OR ge.lemma ILIKE %s
                    ORDER BY v.book_name, v.chapter_num, v.verse_num
                    LIMIT %s
                """, ('%agap%', '%phileo%', '%love%', 5))
                greek_results = cursor.fetchall()
                print(f"   Greek results: {len(greek_results)} rows")
                for r in greek_results[:3]:
                    print(f"     {r['book_name']} {r['chapter_num']}:{r['verse_num']} - {r['word_text']} ({r['strongs_id']})")
            except Exception as e:
                print(f"   Greek query error: {e}")
            
            # Test Hebrew love query (fixed)  
            print("\n2. Testing Hebrew love words query:")
            try:
                cursor.execute("""
                    SELECT DISTINCT
                        hw.verse_id, hw.word_text, hw.strongs_id, hw.transliteration, hw.gloss,
                        he.lemma, he.definition, he.usage, 'Hebrew' as language,
                        v.book_name, v.chapter_num, v.verse_num, v.text, v.translation_source
                    FROM bible.hebrew_ot_words hw
                    JOIN bible.hebrew_entries he ON hw.strongs_id = he.strongs_id
                    JOIN bible.verses v ON hw.verse_id = v.verse_id
                    WHERE hw.strongs_id IN ('H0157', 'H0160', 'H2617')
                    OR he.lemma ILIKE %s OR he.lemma ILIKE %s OR he.lemma ILIKE %s
                    ORDER BY v.book_name, v.chapter_num, v.verse_num
                    LIMIT %s
                """, ('%ahab%', '%chesed%', '%love%', 5))
                hebrew_results = cursor.fetchall()
                print(f"   Hebrew results: {len(hebrew_results)} rows")
                for r in hebrew_results[:3]:
                    print(f"     {r['book_name']} {r['chapter_num']}:{r['verse_num']} - {r['word_text']} ({r['strongs_id']})")
            except Exception as e:
                print(f"   Hebrew query error: {e}")
                
            # Test cross-references query (fixed)
            print("\n3. Testing cross-references query:")
            try:
                cursor.execute("""
                    SELECT DISTINCT
                        vm.source_book, vm.source_chapter, vm.source_verse,
                        vm.target_book, vm.target_chapter, vm.target_verse
                    FROM bible.versification_mappings vm
                    JOIN bible.verses v ON (
                        v.book_name = vm.source_book 
                        AND v.chapter_num::text = vm.source_chapter 
                        AND v.verse_num::text = vm.source_verse
                    )
                    WHERE v.verse_id = ANY(%s)
                    LIMIT 5
                """, ([70757, 130253],))  # Sample verse IDs
                cross_refs = cursor.fetchall()
                print(f"   Cross-reference results: {len(cross_refs)} rows")
                for r in cross_refs[:3]:
                    print(f"     {r['source_book']} {r['source_chapter']}:{r['source_verse']} → {r['target_book']} {r['target_chapter']}:{r['target_verse']}")
            except Exception as e:
                print(f"   Cross-reference query error: {e}")

if __name__ == "__main__":
    test_fixed_queries() 