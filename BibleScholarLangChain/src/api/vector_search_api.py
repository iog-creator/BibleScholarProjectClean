from flask import Blueprint, request, jsonify
import psycopg
from psycopg.rows import dict_row
import requests
import numpy as np
from dotenv import load_dotenv
import sys
import os
from colorama import Fore, init

# Add the project root to path for imports
sys.path.append('C:\\Users\\mccoy\\Documents\\Projects\\Projects\\CursorMCPWorkspace')
from BibleScholarLangChain.src.database.secure_connection import get_secure_connection
from BibleScholarLangChain.scripts.db_config import load_config

init(autoreset=True)
load_dotenv()

vector_search_api = Blueprint('vector_search_api', __name__)

config = load_config()

def get_embedding(text):
    """Generate embeddings using LM Studio API"""
    headers = {"Content-Type": "application/json"}
    data = {"model": config['lm_studio']['models']['embeddings'], "input": text}
    try:
        lm_studio_url = config['lm_studio']['base_url'] + "/embeddings"
        response = requests.post(lm_studio_url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        return [float(val) for val in response.json()['data'][0]['embedding']]
    except Exception as e:
        print(Fore.RED + f"Embedding error: {e}")
        return None

def validate_translation(translation):
    """Validate and normalize translation code"""
    conn = get_secure_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DISTINCT translation_source FROM bible.verse_embeddings")
            valid_translations = [row['translation_source'] for row in cursor.fetchall()]
        if translation in valid_translations:
            return translation
        normalized = translation.upper()
        if normalized in valid_translations:
            return normalized
        print(Fore.YELLOW + f"Invalid translation: {translation}, using KJV")
        return "KJV"
    finally:
        conn.close()

@vector_search_api.route('/vector-search', methods=['GET'])
def vector_search():
    """API endpoint for semantic vector search"""
    try:
        query = request.args.get('q', '')
        translation = validate_translation(request.args.get('translation', 'KJV'))
        limit = min(int(request.args.get('limit', 10)), 50)
        
        if not query:
            return jsonify({"error": "Query parameter 'q' is required"}), 400
            
        embedding = get_embedding(query)
        if not embedding:
            return jsonify({"error": "Failed to generate embedding"}), 500
            
        # Convert embedding to string format for PostgreSQL vector type
        embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"
        
        conn = get_secure_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT e.verse_id, e.book_name, e.chapter_num, e.verse_num, v.verse_text, e.translation_source,
                       1 - (e.embedding <=> %s::vector) as similarity
                FROM bible.verse_embeddings e
                JOIN bible.verses v ON e.verse_id = v.verse_id
                WHERE e.translation_source = %s
                ORDER BY e.embedding <=> %s::vector
                LIMIT %s
            """, (embedding_str, translation, embedding_str, limit))
            results = cursor.fetchall()
        conn.close()
        
        # Convert similarity to float for JSON serialization
        for result in results:
            result['similarity'] = float(result['similarity'])
            
        return jsonify({"results": results})
    except Exception as e:
        print(Fore.RED + f"Vector search error: {e}")
        return jsonify({"error": str(e)}), 500

@vector_search_api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    print(Fore.GREEN + "Vector search API health check OK")
    return jsonify({"status": "ok"}) 