from flask import Blueprint, jsonify, request
import sys
import os
from colorama import Fore, init

# Add the project root to path for imports
sys.path.append('C:\\Users\\mccoy\\Documents\\Projects\\Projects\\CursorMCPWorkspace')
from BibleScholarLangChain.src.database.secure_connection import get_secure_connection

init(autoreset=True)
lexicon_api = Blueprint('lexicon_api', __name__)

@lexicon_api.route('/search', methods=['GET'])
def lexicon_search():
    """
    Search lexicon entries by Strong's ID
    
    Parameters:
    - strongs_id: The Strong's ID to search for (e.g., H430, G3056)
    
    Returns:
    - JSON with lexicon entry details
    """
    strongs_id = request.args.get('strongs_id')
    if not strongs_id:
        return jsonify({"error": "strongs_id parameter is required"}), 400
        
    try:
        conn = get_secure_connection()
        with conn.cursor() as cursor:
            # Determine the appropriate table based on ID prefix
            table = "bible.hebrew_entries" if strongs_id.upper().startswith('H') else "bible.greek_entries"
            word_col = "lemma" if strongs_id.upper().startswith('H') else "lemma"
            
            cursor.execute(
                f"""
                SELECT {word_col}, transliteration, definition
                FROM {table}
                WHERE strongs_id = %s
                """, (strongs_id,)
            )
            result = cursor.fetchone()
        conn.close()
        
        if result:
            return jsonify({
                "entry": {
                    "strongs_id": strongs_id,
                    "lemma": result['lemma'],
                    "transliteration": result['transliteration'],
                    "definition": result['definition']
                }
            }), 200
        return jsonify({"error": "No entry found"}), 404
    except Exception as e:
        print(Fore.RED + f"Lexicon search error: {e}")
        return jsonify({"error": str(e)}), 500

@lexicon_api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    print(Fore.GREEN + "Lexicon API health check OK")
    return jsonify({"status": "ok"}) 