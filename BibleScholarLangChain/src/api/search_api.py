from flask import Blueprint, request, jsonify
import psycopg
from psycopg.rows import dict_row
import sys
import os
from colorama import Fore, init

# Add the project root to path for imports
sys.path.append('C:\\Users\\mccoy\\Documents\\Projects\\Projects\\CursorMCPWorkspace')
from BibleScholarLangChain.src.database.secure_connection import get_secure_connection

init(autoreset=True)
search_api = Blueprint('search_api', __name__)

@search_api.route('/', methods=['GET'])
def search():
    """
    Text-based search endpoint for verses and lexicon entries
    
    Parameters:
    - q: Query string to search for
    - type: Type of search ('verse' or 'lexicon')
    - lang: Language filter for lexicon search ('both', 'hebrew', or 'greek')
    
    Returns:
    - JSON with search results
    """
    q = request.args.get('q', '').strip()
    type_ = request.args.get('type')
    lang = request.args.get('lang', 'both')
    
    if not q or not type_:
        return jsonify({"error": "Parameters 'q' and 'type' are required"}), 400
        
    conn = get_secure_connection()
    try:
        with conn.cursor() as cursor:
            if type_ == 'verse':
                cursor.execute(
                    """
                    SELECT book_name, chapter_num, verse_num, verse_text, translation_source
                    FROM bible.verses
                    WHERE verse_text ILIKE %s
                    LIMIT 50
                    """, (f'%{q}%',)
                )
                verses = cursor.fetchall()
                return jsonify({"verses": verses})
            elif type_ == 'lexicon':
                result = {}
                pattern = f'%{q}%'
                
                if lang in ('both', 'hebrew'):
                    cursor.execute(
                        """
                        SELECT strongs_id, lemma AS word, transliteration, definition
                        FROM bible.hebrew_entries
                        WHERE lemma ILIKE %s OR definition ILIKE %s
                        LIMIT 50
                        """, (pattern, pattern)
                    )
                    result['hebrew'] = cursor.fetchall()
                    
                if lang in ('both', 'greek'):
                    cursor.execute(
                        """
                        SELECT strongs_id, lemma AS word, transliteration, definition
                        FROM bible.greek_entries
                        WHERE lemma ILIKE %s OR definition ILIKE %s
                        LIMIT 50
                        """, (pattern, pattern)
                    )
                    result['greek'] = cursor.fetchall()
                    
                return jsonify({"lexicon": result})
            else:
                return jsonify({"error": f"Unknown search type: {type_}"}), 400
    except Exception as e:
        print(Fore.RED + f"Search error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@search_api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    print(Fore.GREEN + "Search API health check OK")
    return jsonify({"status": "ok"}) 