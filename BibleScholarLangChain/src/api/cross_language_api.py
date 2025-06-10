from flask import Blueprint, jsonify, request
import sys
import os
from colorama import Fore, init

# Add the project root to path for imports
sys.path.append('C:\\Users\\mccoy\\Documents\\Projects\\Projects\\CursorMCPWorkspace')
from BibleScholarLangChain.src.database.secure_connection import get_secure_connection

init(autoreset=True)
cross_language_api = Blueprint('cross_language_api', __name__)

@cross_language_api.route('/terms', methods=['GET'])
def get_terms():
    """
    Get theological terms with cross-language mappings
    
    Parameters:
    - limit: Maximum number of terms to return (default: 20)
    
    Returns:
    - JSON with term mappings
    """
    limit = min(int(request.args.get('limit', 20)), 100)
    
    try:
        conn = get_secure_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT h.strongs_id as hebrew_id, h.lemma as hebrew_term, 
                       h.transliteration as hebrew_transliteration,
                       g.strongs_id as greek_id, g.lemma as greek_term,
                       g.transliteration as greek_transliteration
                FROM bible.hebrew_entries h
                JOIN bible.cross_language_mapping m ON h.strongs_id = m.hebrew_id
                JOIN bible.greek_entries g ON g.strongs_id = m.greek_id
                LIMIT %s
            """, (limit,))
            terms = cursor.fetchall()
        conn.close()
        
        if not terms:
            # Fallback to just returning some terms if no mappings exist
            conn = get_secure_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT strongs_id, lemma, transliteration FROM bible.hebrew_entries LIMIT %s", (limit,))
                hebrew_terms = cursor.fetchall()
                
                cursor.execute("SELECT strongs_id, lemma, transliteration FROM bible.greek_entries LIMIT %s", (limit,))
                greek_terms = cursor.fetchall()
            conn.close()
            
            return jsonify({
                "hebrew_terms": hebrew_terms,
                "greek_terms": greek_terms,
                "note": "Cross-language mappings not available"
            })
            
        return jsonify({"terms": terms})
    except Exception as e:
        print(Fore.RED + f"Cross-language error: {e}")
        return jsonify({"error": str(e)}), 500

@cross_language_api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    print(Fore.GREEN + "Cross-language API health check OK")
    return jsonify({"status": "ok"}) 