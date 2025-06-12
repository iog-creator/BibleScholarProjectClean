#!/usr/bin/env python3
"""
Comprehensive Contextual Insights API with ALL Bible data source integration
Integrates: translations, Strong's, morphology, lexicon, cross-references, semantic search
"""
from flask import Blueprint, request, jsonify
import requests
import time
import os
import sys
import json
import psycopg
from psycopg.rows import dict_row
from colorama import Fore, init
import re

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from BibleScholarLangChain.scripts.db_config import get_lm_studio_config, get_database_url
from BibleScholarLangChain.src.utils.bible_reference_parser import normalize_book_name_to_db

init(autoreset=True)
contextual_insights_bp = Blueprint('contextual_insights', __name__)

SYSTEM_PROMPT = "You are a Bible study assistant. You must only answer questions using the data available in the bible_db database. Do not use your own knowledge, outside sources, or make up content. If the answer is not in the database, respond: 'Sorry, I can only answer using the Bible database. No answer found for your query.'"

def get_db_connection():
    """Get database connection"""
    conn_str = get_database_url()
    return psycopg.connect(conn_str, row_factory=dict_row)

class ComprehensiveBibleAnalyzer:
    """Comprehensive Bible analysis using ALL data sources"""
    
    def __init__(self):
        config = get_lm_studio_config()
        self.base_url = config['base_url']
        self.chat_model = config['models']['chat']
        self.embedding_model = config['models']['embeddings']
        self.timeout = config['timeout']
        self.chat_url = f"{self.base_url}/chat/completions"
        self.embeddings_url = f"{self.base_url}/embeddings"
        self.available_translations = ['KJV', 'ASV', 'YLT', 'TAHOT']
        
        # Mapping from v2 canonical names to our database abbreviations
        self.canonical_to_db = {
            'Genesis': 'Gen',
            'Exodus': 'Exo',
            'Leviticus': 'Lev',
            'Numbers': 'Num',
            'Deuteronomy': 'Deu',
            'Joshua': 'Jos',
            'Judges': 'Jdg',
            'Ruth': 'Rut',
            '1 Samuel': '1Sa',
            '2 Samuel': '2Sa',
            '1 Kings': '1Ki',
            '2 Kings': '2Ki',
            '1 Chronicles': '1Ch',
            '2 Chronicles': '2Ch',
            'Ezra': 'Ezr',
            'Nehemiah': 'Neh',
            'Esther': 'Est',
            'Job': 'Job',
            'Psalms': 'Psa',
            'Proverbs': 'Pro',
            'Ecclesiastes': 'Ecc',
            'Song of Solomon': 'Sng',
            'Isaiah': 'Isa',
            'Jeremiah': 'Jer',
            'Lamentations': 'Lam',
            'Ezekiel': 'Eze',
            'Daniel': 'Dan',
            'Hosea': 'Hos',
            'Joel': 'Joe',
            'Amos': 'Amo',
            'Obadiah': 'Oba',
            'Jonah': 'Jon',
            'Micah': 'Mic',
            'Nahum': 'Nah',
            'Habakkuk': 'Hab',
            'Zephaniah': 'Zep',
            'Haggai': 'Hag',
            'Zechariah': 'Zec',
            'Malachi': 'Mal',
            'Matthew': 'Mat',
            'Mark': 'Mar',
            'Luke': 'Luk',
            'John': 'Jhn',
            'Acts': 'Act',
            'Romans': 'Rom',
            '1 Corinthians': '1Co',
            '2 Corinthians': '2Co',
            'Galatians': 'Gal',
            'Ephesians': 'Eph',
            'Philippians': 'Phi',
            'Colossians': 'Col',
            '1 Thessalonians': '1Th',
            '2 Thessalonians': '2Th',
            '1 Timothy': '1Ti',
            '2 Timothy': '2Ti',
            'Titus': 'Tit',
            'Philemon': 'Phm',
            'Hebrews': 'Heb',
            'James': 'Jam',
            '1 Peter': '1Pe',
            '2 Peter': '2Pe',
            '1 John': '1Jn',
            '2 John': '2Jn',
            '3 John': '3Jn',
            'Jude': 'Jud',
            'Revelation': 'Rev'
        }
    
    def normalize_book_name(self, book_name):
        """Normalize book name to match database format using local parser"""
        if not book_name:
            return book_name
        
        # Use our local comprehensive parser
        db_name = normalize_book_name_to_db(book_name)
        print(f"Book name mapping: {book_name} -> {db_name}")
        return db_name

    def validate_translation(self, translation):
        """Validate that the requested translation is available"""
        if translation not in self.available_translations:
            print(f"Warning: Requested translation '{translation}' not available. Using KJV instead.")
            return 'KJV'
        return translation

    def search_verses_by_keywords(self, keywords, limit=10, translation='KJV'):
        """Search verses using text keywords across all translations including TAHOT"""
        try:
            # Validate translation
            translation = self.validate_translation(translation)
            
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    all_results = []
                    
                    # Search main bible.verses table (KJV, ASV, YLT)
                    cursor.execute("""
                        SELECT DISTINCT v.verse_id, v.book_name, v.chapter_num, v.verse_num, 
                               v.text, v.translation_source
                        FROM bible.verses v
                        WHERE v.text ILIKE %s AND v.translation_source = ANY(%s)
                        ORDER BY v.book_name, v.chapter_num, v.verse_num, v.translation_source
                        LIMIT %s
                    """, (f'%{keywords}%', self.available_translations, limit))
                    main_results = cursor.fetchall()
                    all_results.extend([dict(row) for row in main_results])
                    
                    # Search TAHOT verses separately (tahot_verses_staging table)
                    if 'TAHOT' in self.available_translations:
                        try:
                            cursor.execute("""
                                SELECT DISTINCT 
                                    t.verse_id,
                                    b.book_name,
                                    t.chapter as chapter_num,
                                    t.verse as verse_num,
                                    t.text,
                                    'TAHOT' as translation_source
                                FROM bible.tahot_verses_staging t
                                LEFT JOIN bible.books b ON t.book_id = b.book_id
                                WHERE t.text ILIKE %s
                                ORDER BY b.book_name, t.chapter, t.verse
                                LIMIT %s
                            """, (f'%{keywords}%', max(1, limit // 4)))  # Reserve portion for TAHOT
                            tahot_results = cursor.fetchall()
                            all_results.extend([dict(row) for row in tahot_results])
                            print(f"Found {len(tahot_results)} TAHOT verses for '{keywords}'")
                        except Exception as e:
                            print(f"TAHOT search failed (may be expected if table doesn't exist): {e}")
                    
                    # Sort combined results and limit
                    all_results = sorted(all_results, key=lambda x: (x.get('book_name', ''), x.get('chapter_num', 0), x.get('verse_num', 0)))[:limit]
                    print(f"Total verses found: {len(all_results)} (including TAHOT)")
                    
                    return all_results
        except Exception as e:
            print(f"Error searching verses: {e}")
            return []
    
    def get_love_related_strongs_with_verses(self, limit=20):
        """Get comprehensive love-related Strong's entries with verse context"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Get Hebrew love Strong's with verses
                    cursor.execute("""
                        SELECT DISTINCT
                            hw.strongs_id, hw.gloss, hw.transliteration, he.lemma, he.definition, he.usage,
                            v.verse_id, v.book_name, v.chapter_num, v.verse_num, v.text, v.translation_source,
                            'Hebrew' as language
                        FROM bible.hebrew_ot_words hw
                        JOIN bible.verses v ON hw.verse_id = v.verse_id  
                        LEFT JOIN bible.hebrew_entries he ON hw.strongs_id = he.strongs_id
                        WHERE hw.gloss ILIKE %s AND hw.strongs_id IS NOT NULL
                        ORDER BY v.book_name, v.chapter_num, v.verse_num
                        LIMIT %s
                    """, ('%love%', limit//2))
                    hebrew_results = cursor.fetchall()
                    
                    # Get Greek love Strong's with verses (agape, phileo, etc.)
                    cursor.execute("""
                        SELECT DISTINCT
                            gw.strongs_id, gw.gloss, gw.transliteration, ge.lemma, ge.definition, ge.usage,
                            v.verse_id, v.book_name, v.chapter_num, v.verse_num, v.text, v.translation_source,
                            'Greek' as language
                        FROM bible.greek_nt_words gw
                        JOIN bible.verses v ON gw.verse_id = v.verse_id  
                        LEFT JOIN bible.greek_entries ge ON gw.strongs_id = ge.strongs_id
                        WHERE (gw.gloss ILIKE %s OR gw.word_text ILIKE %s OR gw.word_text ILIKE %s) 
                        AND gw.strongs_id IS NOT NULL
                        ORDER BY v.book_name, v.chapter_num, v.verse_num
                        LIMIT %s
                    """, ('%love%', '%ἀγαπ%', '%φιλ%', limit//2))
                    greek_results = cursor.fetchall()
                    
                    all_results = [dict(row) for row in hebrew_results] + [dict(row) for row in greek_results]
                    return all_results
                    
        except Exception as e:
            print(f"Error getting love-related Strong's with verses: {e}")
            return []

    def get_greek_love_related_strongs_with_verses(self, limit=10):
        """Get Greek love-related Strong's entries (agape, phileo, etc.) with verse context"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT DISTINCT
                            gw.strongs_id, gw.gloss, gw.transliteration, ge.lemma, ge.definition, ge.usage,
                            v.verse_id, v.book_name, v.chapter_num, v.verse_num, v.text, v.translation_source,
                            'Greek' as language
                        FROM bible.greek_nt_words gw
                        JOIN bible.verses v ON gw.verse_id = v.verse_id  
                        LEFT JOIN bible.greek_entries ge ON gw.strongs_id = ge.strongs_id
                        WHERE (gw.gloss ILIKE %s OR gw.word_text ILIKE %s OR gw.word_text ILIKE %s) 
                        AND gw.strongs_id IS NOT NULL
                        ORDER BY v.book_name, v.chapter_num, v.verse_num
                        LIMIT %s
                    """, ('%love%', '%ἀγαπ%', '%φιλ%', limit))
                    return [dict(row) for row in cursor.fetchall()]
                    
        except Exception as e:
            print(f"Error getting Greek love-related Strong's with verses: {e}")
            return []
    
    def get_strongs_analysis(self, verse_ids):
        """Get Strong's number analysis for verses"""
        if not verse_ids:
            return []
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    verse_id_list = tuple(verse_ids)
                    
                    # Get Greek Strong's analysis
                    cursor.execute("""
                        SELECT DISTINCT
                            gw.verse_id, gw.word_text, gw.strongs_id, gw.transliteration, gw.gloss,
                            ge.lemma, ge.definition, ge.usage, 'Greek' as language
                        FROM bible.greek_nt_words gw
                        LEFT JOIN bible.greek_entries ge ON gw.strongs_id = ge.strongs_id
                        WHERE gw.verse_id = ANY(%s) AND gw.strongs_id IS NOT NULL
                        ORDER BY gw.verse_id
                    """, (list(verse_id_list),))
                    greek_analysis = cursor.fetchall()
                    
                    # Get Hebrew Strong's analysis
                    cursor.execute("""
                        SELECT DISTINCT
                            hw.verse_id, hw.word_text, hw.strongs_id, hw.transliteration, hw.gloss,
                            he.lemma, he.definition, he.usage, 'Hebrew' as language
                        FROM bible.hebrew_ot_words hw
                        LEFT JOIN bible.hebrew_entries he ON hw.strongs_id = he.strongs_id
                        WHERE hw.verse_id = ANY(%s) AND hw.strongs_id IS NOT NULL
                        ORDER BY hw.verse_id
                    """, (list(verse_id_list),))
                    hebrew_analysis = cursor.fetchall()
                    
                    all_analysis = [dict(row) for row in greek_analysis] + [dict(row) for row in hebrew_analysis]
                    return all_analysis
        except Exception as e:
            print(f"Error getting Strong's analysis: {e}")
            return []
    
    def get_morphological_analysis(self, verse_ids, query_keyword=""):
        """Get morphological analysis for verses (comprehensive Greek + Hebrew)"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    all_morphology = []
                    
                    # Standard morphological analysis for specific verses
                    if verse_ids:
                        verse_id_list = tuple(verse_ids)
                        
                        # Get Greek morphology
                        cursor.execute("""
                            SELECT DISTINCT
                                gw.verse_id, gw.word_text, gw.grammar_code, gw.transliteration,
                                gw.strongs_id, gw.gloss, v.book_name, v.chapter_num, v.verse_num,
                                'Greek' as language
                            FROM bible.greek_nt_words gw
                            JOIN bible.verses v ON gw.verse_id = v.verse_id
                            WHERE gw.verse_id = ANY(%s) AND gw.grammar_code IS NOT NULL
                            LIMIT 15
                        """, (list(verse_id_list),))
                        greek_morphology = cursor.fetchall()
                        
                        # Get Hebrew morphology
                        cursor.execute("""
                            SELECT DISTINCT
                                hw.verse_id, hw.word_text, hw.grammar_code, hw.transliteration,
                                hw.strongs_id, hw.gloss, v.book_name, v.chapter_num, v.verse_num,
                                'Hebrew' as language
                            FROM bible.hebrew_ot_words hw
                            JOIN bible.verses v ON hw.verse_id = v.verse_id
                            WHERE hw.verse_id = ANY(%s) AND hw.grammar_code IS NOT NULL
                            LIMIT 15
                        """, (list(verse_id_list),))
                        hebrew_morphology = cursor.fetchall()
                        
                        all_morphology.extend([dict(row) for row in greek_morphology])
                        all_morphology.extend([dict(row) for row in hebrew_morphology])
                    
                    # For love queries, add enhanced love word analysis (Greek + Hebrew)
                    if 'love' in query_keyword.lower():
                        print("🔍 Enhanced morphological analysis for love words...")
                        
                        # Hebrew love words
                        cursor.execute("""
                            SELECT DISTINCT
                                hw.verse_id, hw.word_text, hw.grammar_code, hw.transliteration,
                                hw.strongs_id, hw.gloss, v.book_name, v.chapter_num, v.verse_num,
                                'Hebrew' as language
                            FROM bible.hebrew_ot_words hw
                            JOIN bible.verses v ON hw.verse_id = v.verse_id
                            WHERE hw.gloss ILIKE %s AND hw.grammar_code IS NOT NULL
                            ORDER BY v.book_name, v.chapter_num, v.verse_num
                            LIMIT 10
                        """, ('%love%',))
                        hebrew_love_morphology = cursor.fetchall()
                        
                        # Greek love words (agape, phileo, etc.)
                        cursor.execute("""
                            SELECT DISTINCT
                                gw.verse_id, gw.word_text, gw.grammar_code, gw.transliteration,
                                gw.strongs_id, gw.gloss, v.book_name, v.chapter_num, v.verse_num,
                                'Greek' as language
                            FROM bible.greek_nt_words gw
                            JOIN bible.verses v ON gw.verse_id = v.verse_id
                            WHERE (gw.gloss ILIKE %s OR gw.word_text ILIKE %s OR gw.word_text ILIKE %s) 
                            AND gw.grammar_code IS NOT NULL
                            ORDER BY v.book_name, v.chapter_num, v.verse_num
                            LIMIT 10
                        """, ('%love%', '%ἀγαπ%', '%φιλ%'))
                        greek_love_morphology = cursor.fetchall()
                        
                        love_entries = [dict(row) for row in hebrew_love_morphology] + [dict(row) for row in greek_love_morphology]
                        all_morphology.extend(love_entries)
                        
                        if hebrew_love_morphology or greek_love_morphology:
                            print(f"Found {len(hebrew_love_morphology)} Hebrew + {len(greek_love_morphology)} Greek love word morphological entries")
                    
                    return all_morphology
                    
        except Exception as e:
            print(f"Error getting morphological analysis: {e}")
            return []
    
    def get_cross_references(self, verse_ids):
        """Get cross-references and related verses"""
        if not verse_ids:
            return []
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    verse_id_list = tuple(verse_ids)
                    cross_refs = []
                    
                    # Simple approach: Get verses with the same Strong's numbers
                    try:
                        cursor.execute("""
                            SELECT DISTINCT v.verse_id, v.book_name, v.chapter_num, v.verse_num, 
                                   LEFT(v.text, 100) as text_sample, hw.strongs_id
                            FROM bible.verses v
                            JOIN bible.hebrew_ot_words hw ON hw.verse_id = v.verse_id
                            WHERE hw.strongs_id IN (
                                SELECT DISTINCT hw2.strongs_id 
                                FROM bible.hebrew_ot_words hw2 
                                WHERE hw2.verse_id = ANY(%s) AND hw2.strongs_id IS NOT NULL
                            )
                            AND v.verse_id != ALL(%s)
                            LIMIT 5
                        """, (list(verse_id_list), list(verse_id_list)))
                        hebrew_refs = cursor.fetchall()
                        cross_refs.extend([dict(row) for row in hebrew_refs])
                    except Exception as e:
                        print(f"Hebrew cross-ref error: {e}")
                    
                    # Get Greek cross-references
                    try:
                        cursor.execute("""
                            SELECT DISTINCT v.verse_id, v.book_name, v.chapter_num, v.verse_num, 
                                   LEFT(v.text, 100) as text_sample, gw.strongs_id
                            FROM bible.verses v
                            JOIN bible.greek_nt_words gw ON gw.verse_id = v.verse_id
                            WHERE gw.strongs_id IN (
                                SELECT DISTINCT gw2.strongs_id 
                                FROM bible.greek_nt_words gw2 
                                WHERE gw2.verse_id = ANY(%s) AND gw2.strongs_id IS NOT NULL
                            )
                            AND v.verse_id != ALL(%s)
                            LIMIT 5
                        """, (list(verse_id_list), list(verse_id_list)))
                        greek_refs = cursor.fetchall()
                        cross_refs.extend([dict(row) for row in greek_refs])
                    except Exception as e:
                        print(f"Greek cross-ref error: {e}")
                    
                    # Simple versification mapping sample (just to show it exists)
                    try:
                        cursor.execute("""
                            SELECT source_book, source_chapter, source_verse,
                                   target_book, target_chapter, target_verse
                            FROM bible.versification_mappings 
                            LIMIT 3
                        """)
                        version_refs = cursor.fetchall()
                        cross_refs.extend([dict(row) for row in version_refs])
                    except Exception as e:
                        print(f"Versification mapping error: {e}")
                    
                    return cross_refs[:10]  # Limit total results
                    
        except Exception as e:
            print(f"Error getting cross-references: {e}")
            return []
    
    def get_tahot_verses(self, query_text, limit=5):
        """Get TAHOT verses staging data"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT book_id, chapter, verse, LEFT(text, 100) as text_sample
                        FROM bible.tahot_verses_staging
                        WHERE text ILIKE %s
                        LIMIT %s
                    """, (f'%{query_text}%', limit))
                    return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting TAHOT verses: {e}")
            return []
    
    def get_morphology_code_descriptions(self, morphology_data):
        """Get detailed descriptions for morphology codes"""
        if not morphology_data:
            return []
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    all_descriptions = []
                    
                    # Get unique grammar codes
                    greek_codes = [m['grammar_code'] for m in morphology_data if m['language'] == 'Greek' and m.get('grammar_code')]
                    hebrew_codes = [m['grammar_code'] for m in morphology_data if m['language'] == 'Hebrew' and m.get('grammar_code')]
                    
                    # Get Greek morphology descriptions
                    if greek_codes:
                        cursor.execute("""
                            SELECT code, description, part_of_speech, morphology_type
                            FROM bible.greek_morphology_codes
                            WHERE code = ANY(%s)
                        """, (greek_codes,))
                        greek_descriptions = [dict(row) for row in cursor.fetchall()]
                        for desc in greek_descriptions:
                            desc['language'] = 'Greek'
                        all_descriptions.extend(greek_descriptions)
                    
                    # Get Hebrew morphology descriptions  
                    if hebrew_codes:
                        cursor.execute("""
                            SELECT code, description, part_of_speech, morphology_type
                            FROM bible.hebrew_morphology_codes
                            WHERE code = ANY(%s)
                        """, (hebrew_codes,))
                        hebrew_descriptions = [dict(row) for row in cursor.fetchall()]
                        for desc in hebrew_descriptions:
                            desc['language'] = 'Hebrew'
                        all_descriptions.extend(hebrew_descriptions)
                    
                    return all_descriptions
        except Exception as e:
            print(f"Error getting morphology code descriptions: {e}")
            return []
    
    def get_versification_mappings(self, verse_ids, limit=10):
        """Get versification mappings for comprehensive cross-references"""
        if not verse_ids:
            return []
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Check if versification_mappings table exists
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'bible' 
                            AND table_name = 'versification_mappings'
                        )
                    """)
                    table_exists = cursor.fetchone()[0]
                    
                    if not table_exists:
                        print("Versification mappings table does not exist in database")
                        return []
                    
                    # Get book names from verses to search mappings
                    cursor.execute("""
                        SELECT DISTINCT book_name
                        FROM bible.verses
                        WHERE verse_id = ANY(%s)
                    """, (verse_ids,))
                    book_names = [row[0] for row in cursor.fetchall()]
                    
                    if book_names:
                        cursor.execute("""
                            SELECT source_book, source_chapter, source_verse,
                                   target_book, target_chapter, target_verse,
                                   mapping_type, category, notes
                            FROM bible.versification_mappings
                            WHERE source_book = ANY(%s) OR target_book = ANY(%s)
                            LIMIT %s
                        """, (book_names, book_names, limit))
                        return [dict(row) for row in cursor.fetchall()]
                    
                    return []
        except Exception as e:
            print(f"Error getting versification mappings: {e}")
            return []
    
    def get_complete_translation_analysis(self, query, limit=20):
        """Get comprehensive analysis across ALL available translations"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Get all available translations
                    cursor.execute("""
                        SELECT DISTINCT translation_source, COUNT(*) as verse_count
                        FROM bible.verses
                        GROUP BY translation_source
                        ORDER BY verse_count DESC
                    """)
                    available_translations = [dict(row) for row in cursor.fetchall()]
                    
                    # Search across all translations
                    cursor.execute("""
                        SELECT v.translation_source, v.book_name, v.chapter_num, v.verse_num, v.text,
                               COUNT(*) OVER (PARTITION BY v.translation_source) as translation_total
                        FROM bible.verses v
                        WHERE v.text ILIKE %s
                        ORDER BY v.translation_source, v.book_name, v.chapter_num, v.verse_num
                        LIMIT %s
                    """, (f'%{query}%', limit))
                    translation_results = [dict(row) for row in cursor.fetchall()]
                    
                    return {
                        'available_translations': available_translations,
                        'search_results': translation_results
                    }
        except Exception as e:
            print(f"Error getting complete translation analysis: {e}")
            return {'available_translations': [], 'search_results': []}

    def get_semantic_similar_verses(self, query_text, limit=5):
        """Get semantically similar verses using embeddings (bge-m3 + nomic)"""
        try:
            # Get embedding for query
            embedding = self.get_embedding(query_text)
            if not embedding:
                return []
            
            # Format embedding as PostgreSQL vector
            embedding_str = '[' + ','.join(map(str, embedding)) + ']'
            
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    results = []
                    
                    # 1. Search LangChain embeddings (1024-dim, potentially richer data)
                    try:
                        cursor.execute("""
                            SELECT document, cmetadata,
                                   (embedding <-> %s::vector) as similarity_distance
                            FROM public.langchain_pg_embedding
                            WHERE embedding IS NOT NULL
                            ORDER BY embedding <-> %s::vector
                            LIMIT %s
                        """, (embedding_str, embedding_str, limit//2))
                        langchain_results = cursor.fetchall()
                        
                        for result in langchain_results:
                            results.append({
                                'source': 'langchain',
                                'document': result['document'], 
                                'metadata': result['cmetadata'],
                                'similarity_distance': result['similarity_distance']
                            })
                    except Exception as e:
                        print(f"LangChain search failed: {e}")
                    
                    # 2. Search native verse embeddings (768-dim)
                    cursor.execute("""
                        SELECT v.verse_id, v.book_name, v.chapter_num, v.verse_num, 
                               v.text, v.translation_source,
                               (ve.embedding <-> %s::vector) as similarity_distance
                        FROM bible.verses v
                        JOIN bible.verse_embeddings ve ON v.verse_id = ve.verse_id
                        WHERE ve.embedding IS NOT NULL
                        ORDER BY ve.embedding <-> %s::vector
                        LIMIT %s
                    """, (embedding_str, embedding_str, limit))
                    verse_results = cursor.fetchall()
                    
                    for result in verse_results:
                        results.append(dict(result))
                    
                    return results
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []
    
    def get_embedding(self, text):
        """Get embedding for text using LM Studio"""
        try:
            response = requests.post(
                self.embeddings_url,
                json={"input": text, "model": self.embedding_model},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()["data"][0]["embedding"]
            else:
                print(f"Embedding API error: {response.status_code}")
                return None
        except Exception as e:
            print(f"Embedding failed: {e}")
            return None
    
    def generate_comprehensive_analysis(self, query, verses_data, strongs_data, morphology_data, cross_refs_data, semantic_verses, morphology_codes=None, versification_mappings=None, translation_analysis=None):
        """Generate comprehensive analysis using LM Studio"""
        try:
            # Create comprehensive context
            comprehensive_context = self._format_comprehensive_context(
                verses_data, strongs_data, morphology_data, 
                cross_refs_data, semantic_verses, morphology_codes,
                versification_mappings, translation_analysis
            )
            
            # Create comprehensive prompt
            prompt = f"""As a biblical scholar with access to comprehensive biblical resources, provide detailed insights for this query: "{query}"

AVAILABLE TRANSLATIONS (USE ONLY THESE):
- KJV (King James Version)
- ASV (American Standard Version)
- YLT (Young's Literal Translation)
- TAHOT (The Ancient Hebrew Old Testament)

IMPORTANT: Do not reference or quote from any other translations. Use ONLY the translations listed above.

COMPREHENSIVE BIBLICAL DATA AVAILABLE:
{comprehensive_context}

Please provide a thorough analysis that integrates:
1. **Multiple Translation Perspective**: Compare insights across our available translations (KJV, ASV, YLT, TAHOT)
2. **Original Language Analysis**: Use Greek/Hebrew Strong's numbers and lexical data
3. **Grammatical Context**: Apply morphological analysis for deeper understanding
4. **Cross-References**: Connect related passages and themes
5. **Semantic Connections**: Identify conceptually related verses and themes
6. **Theological Implications**: Explain the theological significance
7. **Practical Application**: How this applies to Christian life and understanding

Query: {query}

Provide a comprehensive, scholarly response that demonstrates the depth of biblical analysis possible with these integrated resources. Remember to use ONLY the translations listed above."""

            # Generate response using LM Studio
            response = requests.post(
                self.chat_url,
                json={
                    "model": self.chat_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 8128,
                    "temperature": 0.7
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                return f"Error generating analysis: {response.status_code}"
                
        except Exception as e:
            return f"Error communicating with LM Studio: {e}"

    def _format_comprehensive_context(self, verses_data, strongs_data, morphology_data, cross_refs_data, semantic_verses, morphology_codes, versification_mappings, translation_analysis):
        """Format comprehensive context for LM Studio prompt"""
        context_parts = []
        
        if verses_data:
            context_parts.append("## RELEVANT VERSES FROM MULTIPLE TRANSLATIONS:")
            for verse in verses_data[:10]:  # Limit for readability
                context_parts.append(f"• {verse['book_name']} {verse['chapter_num']}:{verse['verse_num']} ({verse['translation_source']}): {verse['text']}")
        
        if strongs_data:
            context_parts.append("\n## ORIGINAL LANGUAGE ANALYSIS (STRONG'S NUMBERS):")
            greek_strongs = [s for s in strongs_data if s['language'] == 'Greek'][:5]
            hebrew_strongs = [s for s in strongs_data if s['language'] == 'Hebrew'][:5]
            
            if greek_strongs:
                context_parts.append("### Greek Words:")
                for word in greek_strongs:
                    try:
                        word_text = word.get('word_text', word.get('gloss', 'N/A'))
                        lemma = word.get('lemma', 'N/A')
                        definition = word.get('definition', 'N/A')
                        strongs_id = word.get('strongs_id', 'N/A')
                        context_parts.append(f"• {word_text} ({strongs_id}): {lemma} - {definition}")
                    except Exception as e:
                        print(f"Error processing Greek Strong's word: {e}, word data: {word}")
            
            if hebrew_strongs:
                context_parts.append("### Hebrew Words:")
                for word in hebrew_strongs:
                    try:
                        word_text = word.get('word_text', word.get('gloss', 'N/A'))
                        lemma = word.get('lemma', 'N/A')
                        definition = word.get('definition', 'N/A')
                        strongs_id = word.get('strongs_id', 'N/A')
                        context_parts.append(f"• {word_text} ({strongs_id}): {lemma} - {definition}")
                    except Exception as e:
                        print(f"Error processing Hebrew Strong's word: {e}, word data: {word}")
        
        if morphology_data:
            context_parts.append("\n## GRAMMATICAL ANALYSIS (MORPHOLOGY):")
            greek_morph = [m for m in morphology_data if m['language'] == 'Greek'][:5]
            hebrew_morph = [m for m in morphology_data if m['language'] == 'Hebrew'][:5]
            
            if greek_morph:
                context_parts.append("### Greek Grammar:")
                for morph in greek_morph:
                    try:
                        word_text = morph.get('word_text', 'N/A')
                        strongs_id = morph.get('strongs_id', 'N/A')
                        grammar_code = morph.get('grammar_code', 'N/A')
                        gloss = morph.get('gloss', 'N/A')
                        context_parts.append(f"• {word_text} ({strongs_id}) [{grammar_code}]: {gloss}")
                    except Exception as e:
                        print(f"Error processing Greek morphology: {e}, morph data: {morph}")
            
            if hebrew_morph:
                context_parts.append("### Hebrew Grammar:")
                for morph in hebrew_morph:
                    try:
                        word_text = morph.get('word_text', 'N/A')
                        strongs_id = morph.get('strongs_id', 'N/A')
                        grammar_code = morph.get('grammar_code', 'N/A')
                        gloss = morph.get('gloss', 'N/A')
                        ref = f"{morph.get('book_name', '')} {morph.get('chapter_num', '')}:{morph.get('verse_num', '')}" if 'book_name' in morph else ""
                        context_parts.append(f"• {word_text} ({strongs_id}) [{grammar_code}]: {gloss} {ref}".strip())
                    except Exception as e:
                        print(f"Error processing Hebrew morphology: {e}, morph data: {morph}")
        
        if cross_refs_data:
            context_parts.append("\n## CROSS-REFERENCES AND RELATED VERSES:")
            for ref in cross_refs_data[:5]:
                try:
                    if 'reference_type' in ref and ref['reference_type'] == 'strong_reference':
                        # Strong's number cross-reference
                        context_parts.append(f"• {ref['book_name']} {ref['chapter_num']}:{ref['verse_num']}: {ref['text'][:80]}...")
                    elif 'source_book' in ref:
                        # Versification mapping
                        context_parts.append(f"• {ref['source_book']} {ref['source_chapter']}:{ref['source_verse']} → {ref['target_book']} {ref['target_chapter']}:{ref['target_verse']}")
                    else:
                        # Fallback
                        context_parts.append(f"• Cross-reference found")
                except Exception as e:
                    print(f"Error processing cross-reference: {e}, ref data: {ref}")
        
        if semantic_verses:
            context_parts.append("\n## SEMANTICALLY RELATED VERSES (BGE-M3 + NOMIC EMBEDDINGS):")
            for verse in semantic_verses[:5]:
                # Handle both bge-m3 and native verse formats
                if 'source' in verse and verse['source'] == 'bge-m3':
                    context_parts.append(f"• BGE-M3: {verse['document'][:100]}...")
                else:
                    context_parts.append(f"• {verse['book_name']} {verse['chapter_num']}:{verse['verse_num']}: {verse['text'][:100]}...")
        
        if morphology_codes:
            context_parts.append("\n## DETAILED MORPHOLOGICAL CODE DESCRIPTIONS:")
            greek_codes = [c for c in morphology_codes if c['language'] == 'Greek'][:3]
            hebrew_codes = [c for c in morphology_codes if c['language'] == 'Hebrew'][:3]
            
            if greek_codes:
                context_parts.append("### Greek Morphology:")
                for code in greek_codes:
                    context_parts.append(f"• {code['code']}: {code['description']} ({code.get('part_of_speech', 'N/A')})")
            
            if hebrew_codes:
                context_parts.append("### Hebrew Morphology:")
                for code in hebrew_codes:
                    context_parts.append(f"• {code['code']}: {code['description']} ({code.get('part_of_speech', 'N/A')})")
        
        if versification_mappings:
            context_parts.append("\n## VERSIFICATION MAPPINGS:")
            for mapping in versification_mappings[:5]:
                source = f"{mapping['source_book']} {mapping['source_chapter']}:{mapping['source_verse']}"
                target = f"{mapping['target_book']} {mapping['target_chapter']}:{mapping['target_verse']}"
                mapping_type = mapping.get('mapping_type', 'N/A')
                context_parts.append(f"• {source} → {target} ({mapping_type})")
        
        if translation_analysis and translation_analysis.get('available_translations'):
            context_parts.append("\n## COMPLETE TRANSLATION ANALYSIS:")
            translations = translation_analysis['available_translations'][:5]
            context_parts.append(f"Available translations: {', '.join([t['translation_source'] + '(' + str(t['verse_count']) + ')' for t in translations])}")
            
            if translation_analysis.get('search_results'):
                context_parts.append("### Translation Comparison:")
                for result in translation_analysis['search_results'][:5]:
                    context_parts.append(f"• {result['translation_source']}: {result['book_name']} {result['chapter_num']}:{result['verse_num']} - {result['text'][:80]}...")
        
        return "\n".join(context_parts)

    def search_specific_verse(self, verse_reference):
        """Search for a specific verse reference like 'Ephesians 5:4' or 'John 3:16' including TAHOT"""
        try:
            # Parse verse reference (e.g., "Ephesians 5:4", "John 3:16", "1 Corinthians 13:4")
            pattern = r'(\d*\s*\w+)\s+(\d+):(\d+)'
            match = re.match(pattern, verse_reference.strip())
            
            if not match:
                print(f"Could not parse verse reference: {verse_reference}")
                return []
            
            book_name = match.group(1).strip()
            chapter_num = int(match.group(2))
            verse_num = int(match.group(3))
            
            # Normalize book name
            normalized_book = self.normalize_book_name(book_name)
            print(f"Searching for: {book_name} -> {normalized_book} {chapter_num}:{verse_num}")
            
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Try multiple book name variations for better matching
                    book_variations = [
                        normalized_book,
                        book_name,  # Original input
                        book_name.title(),  # Title case
                        book_name.upper(),  # Upper case
                        book_name.lower()   # Lower case
                    ]
                    
                    results = []
                    
                    # Search main bible.verses table
                    for book_variant in book_variations:
                        cursor.execute("""
                            SELECT verse_id, book_name, chapter_num, verse_num, text, translation_source
                            FROM bible.verses 
                            WHERE book_name ILIKE %s AND chapter_num = %s AND verse_num = %s 
                            AND translation_source = ANY(%s)
                            ORDER BY translation_source
                        """, (book_variant, chapter_num, verse_num, self.available_translations))
                        
                        variant_results = cursor.fetchall()
                        if variant_results:
                            results.extend([dict(row) for row in variant_results])
                            print(f"Found {len(variant_results)} verses with book variant '{book_variant}'")
                            break  # Use first successful match
                    
                    # If no exact match, try partial matching
                    if not results:
                        cursor.execute("""
                            SELECT verse_id, book_name, chapter_num, verse_num, text, translation_source
                            FROM bible.verses 
                            WHERE book_name ILIKE %s AND chapter_num = %s AND verse_num = %s 
                            AND translation_source = ANY(%s)
                            ORDER BY translation_source
                        """, (f'%{book_name}%', chapter_num, verse_num, self.available_translations))
                        
                        results = [dict(row) for row in cursor.fetchall()]
                        print(f"Found {len(results)} verses with partial book match")
                    
                    # Search TAHOT verses separately (tahot_verses_staging table)
                    if 'TAHOT' in self.available_translations:
                        try:
                            # Try different book name variations for TAHOT as well
                            for book_variant in book_variations:
                                cursor.execute("""
                                    SELECT DISTINCT 
                                        t.verse_id,
                                        b.book_name,
                                        t.chapter as chapter_num,
                                        t.verse as verse_num,
                                        t.text,
                                        'TAHOT' as translation_source
                                    FROM bible.tahot_verses_staging t
                                    LEFT JOIN bible.books b ON t.book_id = b.book_id
                                    WHERE b.book_name ILIKE %s AND t.chapter = %s AND t.verse = %s
                                    ORDER BY b.book_name, t.chapter, t.verse
                                """, (book_variant, chapter_num, verse_num))
                                
                                tahot_results = cursor.fetchall()
                                if tahot_results:
                                    results.extend([dict(row) for row in tahot_results])
                                    print(f"Found {len(tahot_results)} TAHOT verses with book variant '{book_variant}'")
                                    break
                            
                            # If no exact TAHOT match, try partial matching
                            if not any(r.get('translation_source') == 'TAHOT' for r in results):
                                cursor.execute("""
                                    SELECT DISTINCT 
                                        t.verse_id,
                                        b.book_name,
                                        t.chapter as chapter_num,
                                        t.verse as verse_num,
                                        t.text,
                                        'TAHOT' as translation_source
                                    FROM bible.tahot_verses_staging t
                                    LEFT JOIN bible.books b ON t.book_id = b.book_id
                                    WHERE b.book_name ILIKE %s AND t.chapter = %s AND t.verse = %s
                                    ORDER BY b.book_name, t.chapter, t.verse
                                """, (f'%{book_name}%', chapter_num, verse_num))
                                
                                tahot_partial_results = cursor.fetchall()
                                if tahot_partial_results:
                                    results.extend([dict(row) for row in tahot_partial_results])
                                    print(f"Found {len(tahot_partial_results)} TAHOT verses with partial book match")
                        except Exception as e:
                            print(f"TAHOT specific verse search failed (may be expected if table doesn't exist): {e}")
                    
                    print(f"Found {len(results)} verse variants total (including TAHOT)")
                    return results
                    
        except Exception as e:
            print(f"Error searching specific verse: {e}")
            return []

    def get_proper_names_analysis(self, verse_ids, query_keyword=""):
        """Get proper names and relationships for verses"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Get proper names from the verses - fixed SQL syntax
                    cursor.execute("""
                        SELECT DISTINCT pn.name, pn.hebrew, pn.greek, pn.description, 
                               COUNT(*) as occurrences,
                               v.book_name, v.chapter_num, v.verse_num, v.text, v.translation_source
                        FROM bible.proper_names pn
                        JOIN bible.verses v ON v.text ILIKE ('%' || pn.name || '%')
                        WHERE (v.verse_id = ANY(%s) OR pn.name ILIKE %s)
                        GROUP BY pn.name, pn.hebrew, pn.greek, pn.description, 
                                v.book_name, v.chapter_num, v.verse_num, v.text, v.translation_source
                        ORDER BY occurrences DESC
                        LIMIT 10
                    """, (verse_ids, f'%{query_keyword}%'))
                    proper_names = cursor.fetchall()
                    
                    # Get proper name relationships if table exists
                    try:
                        cursor.execute("""
                            SELECT DISTINCT pnr.name1, pnr.name2, pnr.relationship_type, pnr.description
                            FROM bible.proper_name_relationships pnr
                            WHERE (pnr.name1 ILIKE %s OR pnr.name2 ILIKE %s)
                            LIMIT 10
                        """, (f'%{query_keyword}%', f'%{query_keyword}%'))
                        relationships = cursor.fetchall()
                    except Exception as rel_error:
                        print(f"Proper name relationships table not available: {rel_error}")
                        relationships = []
                    
                    return {
                        'people': [dict(row) for row in proper_names],
                        'relationships': [dict(row) for row in relationships]
                    }
        except Exception as e:
            print(f"Error getting proper names analysis: {e}")
            return {'people': [], 'relationships': []}

    def get_arabic_verses_analysis(self, verse_ids, query_keyword=""):
        """Get Arabic verses if available"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Check if arabic_verses table exists
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'bible' 
                            AND table_name = 'arabic_verses'
                        )
                    """)
                    table_exists = cursor.fetchone()[0]
                    
                    if not table_exists:
                        print("Arabic verses table does not exist in database")
                        return []
                    
                    cursor.execute("""
                        SELECT av.verse_id, av.arabic_text, av.transliteration, 
                               v.book_name, v.chapter_num, v.verse_num, v.translation_source
                        FROM bible.arabic_verses av
                        JOIN bible.verses v ON av.verse_id = v.verse_id
                        WHERE av.verse_id = ANY(%s) OR av.arabic_text ILIKE %s
                        LIMIT 10
                    """, (verse_ids, f'%{query_keyword}%'))
                    return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting Arabic verses analysis: {e}")
            return []

    def get_comprehensive_cross_references(self, verse_ids, query_keyword=""):
        """Get comprehensive cross-references including deep theological connections"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cross_refs = []
                    
                    # Enhanced cross-references for John 1:1 with deeper theological connections
                    if "john 1:1" in query_keyword.lower():
                        # 1. Creation theme connections
                        cursor.execute("""
                            SELECT v.verse_id, v.book_name, v.chapter_num, v.verse_num, 
                                   v.text, v.translation_source, 'creation_theology' as reason
                            FROM bible.verses v
                            WHERE (v.book_name = 'Gen' AND v.chapter_num = 1 AND v.verse_num = 1)
                               OR (v.book_name = 'Pro' AND v.chapter_num = 8 AND v.verse_num IN (22, 23, 30))
                               OR (v.book_name = 'Psa' AND v.chapter_num = 33 AND v.verse_num = 6)
                               OR (v.book_name = 'Psa' AND v.chapter_num = 119 AND v.verse_num = 89)
                               OR (v.book_name = 'Isa' AND v.chapter_num = 55 AND v.verse_num = 11)
                            ORDER BY v.book_name, v.chapter_num, v.verse_num
                        """)
                        cross_refs.extend([dict(row) for row in cursor.fetchall()])
                        
                        # 2. Divine Word/Logos connections
                        cursor.execute("""
                            SELECT v.verse_id, v.book_name, v.chapter_num, v.verse_num, 
                                   v.text, v.translation_source, 'logos_theology' as reason
                            FROM bible.verses v
                            WHERE (v.book_name = 'Psa' AND v.chapter_num = 107 AND v.verse_num = 20)
                               OR (v.book_name = 'Isa' AND v.chapter_num = 40 AND v.verse_num = 8)
                               OR (v.book_name = 'Jer' AND v.chapter_num = 1 AND v.verse_num IN (4, 9, 12))
                               OR (v.book_name = 'Eze' AND v.chapter_num = 1 AND v.verse_num = 3)
                               OR (v.book_name = 'Heb' AND v.chapter_num = 4 AND v.verse_num = 12)
                            ORDER BY v.book_name, v.chapter_num, v.verse_num
                        """)
                        cross_refs.extend([dict(row) for row in cursor.fetchall()])
                        
                        # 3. Deity/Trinity connections  
                        cursor.execute("""
                            SELECT v.verse_id, v.book_name, v.chapter_num, v.verse_num, 
                                   v.text, v.translation_source, 'deity_theology' as reason
                            FROM bible.verses v
                            WHERE (v.book_name = 'Isa' AND v.chapter_num = 9 AND v.verse_num = 6)
                               OR (v.book_name = 'Mic' AND v.chapter_num = 5 AND v.verse_num = 2)
                               OR (v.book_name = 'Mal' AND v.chapter_num = 3 AND v.verse_num = 6)
                               OR (v.book_name = 'Col' AND v.chapter_num = 1 AND v.verse_num IN (15, 16, 17))
                               OR (v.book_name = 'Heb' AND v.chapter_num = 1 AND v.verse_num IN (1, 2, 3))
                            ORDER BY v.book_name, v.chapter_num, v.verse_num
                        """)
                        cross_refs.extend([dict(row) for row in cursor.fetchall()])
                        
                    # Enhanced "beginning" theme connections
                    elif "beginning" in query_keyword.lower():
                        cursor.execute("""
                            SELECT v.verse_id, v.book_name, v.chapter_num, v.verse_num, 
                                   v.text, v.translation_source, 'beginning_theme' as reason
                            FROM bible.verses v
                            WHERE (v.text ILIKE '%beginning%' AND v.book_name IN ('Gen', 'Pro', 'Ecc', 'Isa', 'Jhn', 'Rev'))
                               OR (v.book_name = 'Rev' AND v.chapter_num = 21 AND v.verse_num = 6)
                               OR (v.book_name = 'Rev' AND v.chapter_num = 22 AND v.verse_num = 13)
                            ORDER BY v.book_name, v.chapter_num, v.verse_num
                            LIMIT 15
                        """)
                        cross_refs.extend([dict(row) for row in cursor.fetchall()])
                    
                    # Strong's number based cross-references for Greek NT
                    if verse_ids:
                        cursor.execute("""
                            SELECT DISTINCT v2.verse_id, v2.book_name, v2.chapter_num, v2.verse_num, 
                                   v2.text, v2.translation_source, 'greek_strongs_connection' as reason,
                                   gw.strongs_id, gw.gloss
                            FROM bible.verses v1
                            JOIN bible.greek_nt_words gw ON v1.verse_id = gw.verse_id
                            JOIN bible.greek_nt_words gw2 ON gw.strongs_id = gw2.strongs_id
                            JOIN bible.verses v2 ON gw2.verse_id = v2.verse_id
                            WHERE v1.verse_id = ANY(%s) AND v2.verse_id != v1.verse_id
                            ORDER BY v2.book_name, v2.chapter_num, v2.verse_num
                            LIMIT 10
                        """, (verse_ids,))
                        cross_refs.extend([dict(row) for row in cursor.fetchall()])
                        
                        # Hebrew OT connections for thematic bridging
                        cursor.execute("""
                            SELECT DISTINCT v.verse_id, v.book_name, v.chapter_num, v.verse_num, 
                                   v.text, v.translation_source, 'hebrew_thematic_bridge' as reason,
                                   hw.strongs_id, hw.gloss
                            FROM bible.hebrew_ot_words hw
                            JOIN bible.verses v ON hw.verse_id = v.verse_id
                            WHERE hw.strongs_id IN ('H1697', 'H430', 'H7225', 'H1254', 'H1961')
                            AND v.book_name IN ('Gen', 'Psa', 'Pro', 'Isa', 'Jer')
                            ORDER BY v.book_name, v.chapter_num, v.verse_num
                            LIMIT 15
                        """)
                        cross_refs.extend([dict(row) for row in cursor.fetchall()])
                    
                    return cross_refs[:25]  # Limit to 25 most relevant
        except Exception as e:
            print(f"Error getting comprehensive cross-references: {e}")
            return []

    def generate_structured_json_analysis(self, query, verses_data, strongs_data, morphology_data, 
                                        cross_refs_data, semantic_verses, proper_names_data, 
                                        arabic_verses_data, morphology_codes=None, 
                                        versification_mappings=None, translation_analysis=None):
        """Generate structured JSON output for second AI agent semantic translation"""
        try:
            start_time = time.time()
            
            # Parse query to determine if it's a verse reference
            verse_pattern = r'(\d*\s*\w+)\s+(\d+):(\d+)'
            is_verse_reference = bool(re.search(verse_pattern, query))
            
            # Generate LM Studio analysis for summary and theological terms
            lm_analysis = self.generate_comprehensive_analysis(
                query, verses_data, strongs_data, morphology_data,
                cross_refs_data, semantic_verses, morphology_codes,
                versification_mappings, translation_analysis
            )
            
            # Parse LM Studio response to extract structured data
            summary = "Comprehensive biblical analysis of the query."
            theological_terms = {}
            historical_context = "Biblical context from database analysis."
            
            # Try to extract structured information from LM Studio response
            if isinstance(lm_analysis, str) and lm_analysis:
                lines = lm_analysis.split('\n')
                current_section = None
                
                for line in lines:
                    line = line.strip()
                    if "summary" in line.lower() or "overview" in line.lower():
                        current_section = "summary"
                    elif "theological" in line.lower() or "terms" in line.lower():
                        current_section = "theological_terms"
                    elif "historical" in line.lower() or "context" in line.lower():
                        current_section = "historical_context"
                    elif line and current_section == "summary" and len(line) > 20:
                        summary = line
                        current_section = None
                    elif line and current_section == "historical_context" and len(line) > 20:
                        historical_context = line
                        current_section = None
            
            # Build structured JSON response
            structured_response = {
                "input": {
                    "reference": query,
                    "type": "verse" if is_verse_reference else "keyword"
                },
                "insights": {
                    "summary": summary,
                    "theological_terms": self._extract_theological_terms(query, strongs_data, verses_data),
                    "cross_references": self._format_cross_references(cross_refs_data),
                    "historical_context": historical_context,
                    "original_language_notes": self._format_original_language_notes(strongs_data, morphology_data),
                    "related_entities": proper_names_data,
                    "translation_variants": self._format_translation_variants(verses_data),
                    "lexical_data": self._format_lexical_data(strongs_data),
                    "semantic_matches": self._format_semantic_matches(semantic_verses),
                    "versification_mappings": self._format_versification_mappings(versification_mappings),
                    "proper_names": self._format_proper_names(proper_names_data),
                    "morphology_codes": self._format_morphology_codes(morphology_codes),
                    "arabic_data": arabic_verses_data if arabic_verses_data else []
                },
                "processing_time_seconds": round(time.time() - start_time, 1)
            }
            
            return structured_response
            
        except Exception as e:
            print(f"Error generating structured JSON analysis: {e}")
            return {
                "input": {"reference": query, "type": "error"},
                "insights": {"summary": f"Error generating analysis: {str(e)}"},
                "processing_time_seconds": 0.0
            }

    def _extract_theological_terms(self, query, strongs_data, verses_data):
        """Extract theological terms from Strong's data and verses"""
        terms = {}
        
        # Key theological terms for common queries
        if "john 1:1" in query.lower():
            terms = {
                "Logos": "The divine Word or reason, embodying God's creative power",
                "God": "The Supreme Being, Creator",
                "Creation": "The act of God bringing the universe into existence"
            }
        elif "beginning" in query.lower():
            terms = {
                "Beginning": "The starting point of creation and divine action",
                "Creation": "God's act of bringing everything into existence",
                "Word": "Divine expression and creative power"
            }
        
        # Add terms from Strong's data
        for strong in strongs_data[:5]:
            if strong.get('definition'):
                key = strong.get('lemma', strong.get('gloss', 'Unknown'))
                terms[key] = strong.get('definition', 'No definition available')
        
        return terms

    def _format_cross_references(self, cross_refs_data):
        """Format cross-references for structured output"""
        formatted_refs = []
        
        for ref in cross_refs_data[:10]:
            formatted_ref = {
                "reference": f"{ref['book_name']} {ref['chapter_num']}:{ref['verse_num']}",
                "text": ref.get('text', '')[:200] + ('...' if len(ref.get('text', '')) > 200 else ''),
                "reason": ref.get('reason', 'Related passage'),
                "translation": ref.get('translation_source', 'KJV')
            }
            formatted_refs.append(formatted_ref)
        
        return formatted_refs

    def _format_original_language_notes(self, strongs_data, morphology_data):
        """Format original language notes with Greek and Hebrew data"""
        notes = []
        
        # Process Strong's data
        for strong in strongs_data[:10]:
            note = {
                "word": strong.get('word_text', strong.get('gloss', 'N/A')),
                "strongs_id": strong.get('strongs_id', 'N/A'),
                "meaning": strong.get('definition', strong.get('gloss', 'N/A')),
                "grammar_code": strong.get('grammar_code', 'N/A'),
                "lemma": strong.get('lemma', 'N/A'),
                "transliteration": strong.get('transliteration', 'N/A'),
                "usage": strong.get('usage', 'Biblical usage'),
                "language": strong.get('language', 'Unknown')
            }
            notes.append(note)
        
        # Add morphology data
        for morph in morphology_data[:5]:
            if not any(n['strongs_id'] == morph.get('strongs_id') for n in notes):
                note = {
                    "word": morph.get('word_text', 'N/A'),
                    "strongs_id": morph.get('strongs_id', 'N/A'),
                    "meaning": morph.get('gloss', 'N/A'),
                    "grammar_code": morph.get('grammar_code', 'N/A'),
                    "lemma": morph.get('lemma', 'N/A'),
                    "transliteration": morph.get('transliteration', 'N/A'),
                    "usage": "Grammatical analysis",
                    "language": morph.get('language', 'Unknown')
                }
                notes.append(note)
        
        return notes

    def _format_translation_variants(self, verses_data):
        """Format translation variants"""
        variants = []
        
        for verse in verses_data:
            variant = {
                "translation": verse.get('translation_source', 'KJV'),
                "text": verse.get('text', '')
            }
            variants.append(variant)
        
        return variants

    def _format_lexical_data(self, strongs_data):
        """Format lexical data for structured output"""
        lexical = []
        
        for strong in strongs_data[:10]:
            lex_entry = {
                "word": strong.get('word_text', strong.get('gloss', 'N/A')),
                "strongs_id": strong.get('strongs_id', 'N/A'),
                "lemma": strong.get('lemma', 'N/A'),
                "transliteration": strong.get('transliteration', 'N/A'),
                "definition": strong.get('definition', strong.get('gloss', 'N/A')),
                "morphology": {
                    "code": strong.get('grammar_code', 'N/A'),
                    "description": strong.get('grammar_description', 'N/A')
                }
            }
            lexical.append(lex_entry)
        
        return lexical

    def _format_semantic_matches(self, semantic_verses):
        """Format semantic matches"""
        matches = []
        
        for verse in semantic_verses[:10]:
            if 'source' in verse and verse['source'] == 'bge-m3':
                match = {
                    "reference": "Semantic Match",
                    "text": verse['document'][:150] + ('...' if len(verse['document']) > 150 else ''),
                    "similarity": verse.get('similarity', 0.0),
                    "translation": "BGE-M3"
                }
            else:
                match = {
                    "reference": f"{verse['book_name']} {verse['chapter_num']}:{verse['verse_num']}",
                    "text": verse['text'][:150] + ('...' if len(verse['text']) > 150 else ''),
                    "similarity": verse.get('similarity', 0.0),
                    "translation": verse.get('translation_source', 'KJV')
                }
            matches.append(match)
        
        return matches

    def _format_versification_mappings(self, versification_mappings):
        """Format versification mappings"""
        if not versification_mappings:
            return []
        
        mappings = []
        for mapping in versification_mappings[:10]:
            formatted_mapping = {
                "source": f"{mapping['source_book']} {mapping['source_chapter']}:{mapping['source_verse']}",
                "target": f"{mapping['target_book']} {mapping['target_chapter']}:{mapping['target_verse']}",
                "type": mapping.get('mapping_type', 'Unknown')
            }
            mappings.append(formatted_mapping)
        
        return mappings

    def _format_proper_names(self, proper_names_data):
        """Format proper names data"""
        if not proper_names_data or not proper_names_data.get('people'):
            return []
        
        formatted_names = []
        for person in proper_names_data['people'][:10]:
            formatted_name = {
                "name": person.get('name', 'Unknown'),
                "hebrew": person.get('hebrew', ''),
                "greek": person.get('greek', ''),
                "description": person.get('description', ''),
                "occurrences": person.get('occurrences', 0)
            }
            formatted_names.append(formatted_name)
        
        return formatted_names

    def _format_morphology_codes(self, morphology_codes):
        """Format morphology codes"""
        if not morphology_codes:
            return []
        
        formatted_codes = []
        for code in morphology_codes[:10]:
            formatted_code = {
                "code": code.get('code', 'N/A'),
                "description": code.get('description', 'N/A'),
                "language": code.get('language', 'Unknown')
            }
            formatted_codes.append(formatted_code)
        
        return formatted_codes

@contextual_insights_bp.route('/insights', methods=['POST'])
def get_comprehensive_insights():
    """Get comprehensive biblical insights using ALL data sources"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data.get('query', '').strip()
        if not query:
            return jsonify({'error': 'Query cannot be empty'}), 400
        
        # Get requested translation, default to KJV
        translation = data.get('translation', 'KJV')
        
        print(f"Processing comprehensive analysis for: {query} (Translation: {translation})")
        
        # Initialize comprehensive analyzer
        analyzer = ComprehensiveBibleAnalyzer()
        
        # Validate translation
        translation = analyzer.validate_translation(translation)
        print(f"Using translation: {translation}")
        
        # Check if query is a specific verse reference (e.g., "Ephesians 5:4")
        verse_pattern = r'(\d*\s*\w+)\s+(\d+):(\d+)'
        if re.search(verse_pattern, query):
            print("Detected verse reference, using specific verse search")
            verses_data = analyzer.search_specific_verse(query)
        else:
            print("Using keyword search")
            # 1. Search verses by keywords
            verses_data = analyzer.search_verses_by_keywords(query, limit=15, translation=translation)
        
        print(f"Found {len(verses_data)} verses")
        
        if not verses_data:
            return jsonify({
                'insights': f"No verses found for query: {query}. Please check the spelling or try a different search term.",
                'query': query,
                'translation': translation,
                'verses_found': 0
            })
        
        # Extract verse IDs for further analysis
        verse_ids = [verse['verse_id'] for verse in verses_data]
        
        # 2. Get Strong's analysis
        print("Getting Strong's analysis...")
        strongs_data = analyzer.get_strongs_analysis(verse_ids)
        print(f"Found {len(strongs_data)} Strong's entries")
        
        # 3. Get morphological analysis
        print("Getting morphological analysis...")
        morphology_data = analyzer.get_morphological_analysis(verse_ids, query)
        print(f"Found {len(morphology_data)} morphological entries")
        
        # 4. Get comprehensive cross-references (including Old Testament links)
        print("Getting comprehensive cross-references...")
        cross_refs_data = analyzer.get_comprehensive_cross_references(verse_ids, query)
        print(f"Found {len(cross_refs_data)} comprehensive cross-references")
        
        # 5. Get semantic similar verses
        print("Getting semantic similar verses...")
        semantic_verses = analyzer.get_semantic_similar_verses(query, limit=5)
        print(f"Found {len(semantic_verses)} semantic matches")
        
        # 6. Get proper names analysis
        print("Getting proper names analysis...")
        proper_names_data = analyzer.get_proper_names_analysis(verse_ids, query)
        print(f"Found {len(proper_names_data.get('people', []))} proper names")
        
        # 7. Get Arabic verses analysis
        print("Getting Arabic verses analysis...")
        arabic_verses_data = analyzer.get_arabic_verses_analysis(verse_ids, query)
        print(f"Found {len(arabic_verses_data)} Arabic verses")
        
        # 8. Get morphology code descriptions
        print("Getting morphology code descriptions...")
        morphology_codes = analyzer.get_morphology_code_descriptions(morphology_data)
        print(f"Found {len(morphology_codes)} morphology code descriptions")
        
        # 9. Get versification mappings
        print("Getting versification mappings...")
        versification_mappings = analyzer.get_versification_mappings(verse_ids, limit=10)
        print(f"Found {len(versification_mappings)} versification mappings")
        
        # 10. Get complete translation analysis
        print("Getting complete translation analysis...")
        translation_analysis = analyzer.get_complete_translation_analysis(query, limit=20)
        print(f"Translation analysis complete")
        
        # 11. Generate structured JSON analysis for second AI agent
        print("Generating structured JSON analysis...")
        structured_analysis = analyzer.generate_structured_json_analysis(
            query, verses_data, strongs_data, morphology_data, 
            cross_refs_data, semantic_verses, proper_names_data,
            arabic_verses_data, morphology_codes, versification_mappings, 
            translation_analysis
        )
        
        print("Structured analysis complete")
        
        return jsonify(structured_analysis)
        
    except Exception as e:
        print(f"Error in comprehensive insights: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@contextual_insights_bp.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok', 
        'server': 'Comprehensive Contextual Insights API',
        'timestamp': time.time(),
        'features': [
            'multi_translation_search',
            'strongs_number_analysis', 
            'morphological_analysis',
            'cross_references',
            'semantic_search',
            'comprehensive_integration'
        ]
    })

@contextual_insights_bp.route('/test_comprehensive')
def test_comprehensive():
    """Test comprehensive functionality"""
    try:
        analyzer = ComprehensiveBibleAnalyzer()
        
        # Test all components
        test_query = "love"
        verses = analyzer.search_verses_by_keywords(test_query, limit=3)
        verse_ids = [v['verse_id'] for v in verses] if verses else []
        
        strongs = analyzer.get_strongs_analysis(verse_ids)
        morphology = analyzer.get_morphological_analysis(verse_ids)
        cross_refs = analyzer.get_cross_references(verse_ids)
        semantic = analyzer.get_semantic_similar_verses(test_query, limit=2)
        
        return jsonify({
            'status': 'success',
            'test_results': {
                'verses_found': len(verses),
                'strongs_entries': len(strongs),
                'morphology_entries': len(morphology),
                'cross_references': len(cross_refs),
                'semantic_matches': len(semantic)
            },
            'sample_data': {
                'verse_sample': verses[0] if verses else None,
                'strongs_sample': strongs[0] if strongs else None,
                'morphology_sample': morphology[0] if morphology else None
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500 