#!/usr/bin/env python3
"""
Vector Search Demo Application

This is a simple web application that demonstrates the vector search capabilities
of the BibleScholarProject. It allows users to search for Bible verses semantically
using pgvector in PostgreSQL.

The demo includes:
- Basic vector search with relevance scoring
- Cross-translation comparison
- Search for verses similar to a reference verse
"""

import os
import sys
import logging
import json
from typing import List, Dict, Any, Optional
import psycopg
from psycopg.rows import dict_row
import numpy as np
import requests
from flask import Flask, request, render_template, jsonify
from dotenv import load_dotenv
from src.config.loader import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/vector_search_demo.log", mode="a"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# LM Studio API settings
config = get_config()
EMBEDDING_MODEL = config.vector_search.embedding_model
LM_STUDIO_EMBEDDINGS_URL = config.api.lm_studio_url
EMBEDDING_PROMPT = config.vector_search.embedding_prompt

# Database connection settings
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "bible_db")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")

# Create Flask app
# app = Flask(__name__)

# Add templates directory
# app.template_folder = "templates"

def get_db_connection():
    """Get a connection to the database."""
    try:
        conn = psycopg.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            row_factory=dict_row
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

def get_embedding(text):
    """
    Get embedding vector for text using LM Studio API.
    
    Args:
        text: Text to encode
        
    Returns:
        List of floats representing the embedding vector
    """
    headers = {"Content-Type": "application/json"}
    data = {"model": EMBEDDING_MODEL, "input": text}
    print(f"Teaching Mode: Sending embedding request to {LM_STUDIO_EMBEDDINGS_URL} with model {EMBEDDING_MODEL}")
    try:
        response = requests.post(LM_STUDIO_EMBEDDINGS_URL, headers=headers, json=data, timeout=10)
    except requests.Timeout:
        print("Teaching Mode: LM Studio embedding request timed out after 10 seconds.")
        return None
    except Exception as e:
        print(f"Teaching Mode: Error calling LM Studio for embedding: {e}")
        return None
    print(f"Teaching Mode: Received embedding response with status {response.status_code}")
    if response.status_code != 200:
        logger.error(f"Error from LM Studio API: {response.status_code} - {response.text}")
        return None
    data = response.json()
    if "data" in data and len(data["data"]) > 0 and "embedding" in data["data"][0]:
        embedding = [float(val) for val in data["data"][0]["embedding"]]
        return embedding
    else:
        logger.error(f"Unexpected response format: {data}")
        return None

def validate_translation(translation):
    """Validate and normalize translation code."""
    # Get list of valid translations
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT translation_source FROM bible.verse_embeddings")
        valid_translations = [row['translation_source'] for row in cursor.fetchall()]
        conn.close()
        
        # Check if the provided translation is valid
        if translation in valid_translations:
            return translation
        
        # If not valid, normalize and check again
        normalized = translation.upper()
        if normalized in valid_translations:
            return normalized
        
        # Return default translation if not found
        logger.warning(f"Invalid translation: {translation}, using KJV")
        return "KJV"
    except Exception as e:
        logger.error(f"Error validating translation: {e}")
        return "KJV"

def search_similar_verses(verse_reference, translation="KJV", limit=10):
    """
    Search for verses similar to the specified verse reference.
    
    Args:
        verse_reference: Reference in format "Book Chapter:Verse" (e.g., "John 3:16")
        translation: Bible translation
        limit: Maximum number of results
        
    Returns:
        List of similar verses
    """
    try:
        # Parse the verse reference
        parts = verse_reference.strip().split()
        if len(parts) < 2:
            logger.error(f"Invalid verse reference format: {verse_reference}")
            return []
        
        book_name = " ".join(parts[:-1])
        chapter_verse = parts[-1].split(":")
        
        if len(chapter_verse) != 2:
            logger.error(f"Invalid verse reference format: {verse_reference}")
            return []
        
        chapter_num = int(chapter_verse[0])
        verse_num = int(chapter_verse[1])
        
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get the embedding for the reference verse
        query = """
        SELECT ve.embedding
        FROM bible.verses v
        JOIN bible.books b ON v.book_name = b.name
        JOIN bible.verse_embeddings ve ON v.verse_id = ve.verse_id
        WHERE b.name = %s
        AND v.chapter_num = %s
        AND v.verse_num = %s
        AND ve.translation_source = %s
        LIMIT 1
        """
        
        cursor.execute(query, (book_name, chapter_num, verse_num, translation))
        result = cursor.fetchone()
        
        if not result:
            logger.error(f"Verse not found: {verse_reference}")
            conn.close()
            return []
        
        # Get the embedding vector
        embedding = result['embedding']
        
        # Search for similar verses
        search_query = """
        SELECT v.verse_id, b.name as book_name, v.chapter_num, v.verse_num, 
               v.text as verse_text, ve.translation_source,
               1 - (ve.embedding <=> %s) as similarity
        FROM bible.verses v
        JOIN bible.books b ON v.book_name = b.name
        JOIN bible.verse_embeddings ve ON v.verse_id = ve.verse_id
        WHERE ve.translation_source = %s
        AND NOT (b.name = %s AND v.chapter_num = %s AND v.verse_num = %s)
        ORDER BY ve.embedding <=> %s
        LIMIT %s
        """
        
        cursor.execute(search_query, (embedding, translation, book_name, chapter_num, verse_num, embedding, limit))
        results = cursor.fetchall()
        
        # Close the connection
        conn.close()
        
        # Convert to list of dictionaries
        return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Error searching for similar verses: {e}")
        return []

def compare_translations(verse_reference, translations=None, limit=5):
    """
    Compare translations of a specific verse using vector similarity.
    
    Args:
        verse_reference: Reference in format "Book Chapter:Verse" (e.g., "John 3:16")
        translations: List of translation codes (e.g., ["KJV", "ASV"])
        limit: Maximum number of translations to compare
        
    Returns:
        Dictionary with verse information and comparisons
    """
    try:
        # Set default translations if not provided
        if not translations:
            translations = ["KJV", "ASV", "WEB"]
        
        # Parse the verse reference
        parts = verse_reference.strip().split()
        if len(parts) < 2:
            logger.error(f"Invalid verse reference format: {verse_reference}")
            return {}
        
        book_name = " ".join(parts[:-1])
        chapter_verse = parts[-1].split(":")
        
        if len(chapter_verse) != 2:
            logger.error(f"Invalid verse reference format: {verse_reference}")
            return {}
        
        chapter_num = int(chapter_verse[0])
        verse_num = int(chapter_verse[1])
        
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all available translations for this verse
        query = """
        SELECT v.verse_id, b.name as book_name, v.chapter_num, v.verse_num, 
               v.text as verse_text, ve.translation_source, ve.embedding
        FROM bible.verses v
        JOIN bible.books b ON v.book_name = b.name
        JOIN bible.verse_embeddings ve ON v.verse_id = ve.verse_id
        WHERE b.name = %s
        AND v.chapter_num = %s
        AND v.verse_num = %s
        ORDER BY ve.translation_source
        """
        
        cursor.execute(query, (book_name, chapter_num, verse_num))
        results = cursor.fetchall()
        
        if not results:
            logger.error(f"Verse not found: {verse_reference}")
            conn.close()
            return {}
        
        # Convert to list of dictionaries
        verses = [dict(row) for row in results]
        
        # Filter to requested translations if specified
        if translations:
            verses = [v for v in verses if v['translation_source'] in translations]
        
        # Limit the number of translations
        if len(verses) > limit:
            verses = verses[:limit]
        
        # Calculate similarity between translations
        similarities = []
        for i, verse1 in enumerate(verses):
            for j, verse2 in enumerate(verses):
                if i >= j:
                    continue
                
                # Calculate cosine similarity manually
                embedding1 = verse1['embedding']
                embedding2 = verse2['embedding']
                
                # Calculate similarity
                similarity = 1 - np.arccos(
                    np.dot(embedding1, embedding2) / 
                    (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
                ) / np.pi
                
                similarities.append({
                    'translation1': verse1['translation_source'],
                    'translation2': verse2['translation_source'],
                    'similarity': float(similarity)
                })
        
        # Close the connection
        conn.close()
        
        # Prepare the result
        result = {
            'reference': verse_reference,
            'verses': [
                {
                    'translation': v['translation_source'],
                    'text': v['verse_text']
                }
                for v in verses
            ],
            'similarities': similarities
        }
        
        return result
    except Exception as e:
        logger.error(f"Error comparing translations: {e}")
        return {}

def vector_search(query, translation="KJV", limit=10):
    """
    Perform vector search for Bible verses.
    
    Args:
        query: Search query
        translation: Bible translation to search
        limit: Maximum number of results
        
    Returns:
        List of verse dictionaries
    """
    try:
        # Get embedding for the query
        embedding = get_embedding(query)
        if not embedding:
            return []
        
        # Convert embedding to string format for PostgreSQL
        embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"
        
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Execute the search query
        search_query = """
        SELECT v.verse_id, b.name as book_name, v.chapter_num, v.verse_num, 
               v.text as verse_text, ve.translation_source,
               1 - (ve.embedding <=> %s::vector) as similarity
        FROM bible.verses v
        JOIN bible.books b ON v.book_name = b.name
        JOIN bible.verse_embeddings ve ON v.verse_id = ve.verse_id
        WHERE ve.translation_source = %s
        ORDER BY ve.embedding <=> %s::vector
        LIMIT %s
        """
        
        cursor.execute(search_query, (embedding_str, translation, embedding_str, limit))
        results = cursor.fetchall()
        
        # Log the top similarity scores for debugging
        for row in results:
            sim = row['similarity'] if isinstance(row, dict) else row[6]
            ref = f"{row['book_name']} {row['chapter_num']}:{row['verse_num']}" if isinstance(row, dict) else f"{row[1]} {row[2]}:{row[3]}"
            logger.info(f"[DEBUG] Query='{query}' Translation='{translation}' Ref={ref} Similarity={sim}")
        
        # Close the connection
        conn.close()
        
        # Convert to list of dictionaries
        return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Error in vector search: {e}")
        return []

if __name__ == "__main__":
    app = Flask(__name__)
    app.template_folder = "templates"

    @app.route("/")
    def index():
        """Render the main demo page."""
        return render_template("vector_search_demo.html")

    @app.route("/search/vector")
    def search_api():
        """API endpoint for vector search."""
        try:
            query = request.args.get("q", "")
            translation = request.args.get("translation", "KJV")
            limit = int(request.args.get("limit", 10))
            
            # Validate translation
            translation = validate_translation(translation)
            
            # Perform the search
            results = vector_search(query, translation, limit)
            
            # Return JSON response
            return jsonify({
                "query": query,
                "translation": translation,
                "results": results
            })
        except Exception as e:
            logger.error(f"Error in search API: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/search/similar")
    def similar_verses_api():
        """API endpoint for finding similar verses."""
        try:
            reference = request.args.get("reference", "")
            translation = request.args.get("translation", "KJV")
            limit = int(request.args.get("limit", 10))
            
            # Validate inputs
            if not reference:
                return jsonify({"error": "No verse reference provided"}), 400
            
            translation = validate_translation(translation)
            
            # Perform the search
            results = search_similar_verses(reference, translation, limit)
            
            # Return JSON response
            return jsonify({
                "reference": reference,
                "translation": translation,
                "results": results
            })
        except Exception as e:
            logger.error(f"Error in similar verses API: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/compare/translations")
    def compare_translations_api():
        """API endpoint for comparing translations."""
        try:
            reference = request.args.get("reference", "")
            translations_param = request.args.get("translations", "KJV,ASV,WEB")
            
            # Validate inputs
            if not reference:
                return jsonify({"error": "No verse reference provided"}), 400
            
            # Parse translations
            translations = [t.strip() for t in translations_param.split(",")]
            
            # Perform the comparison
            result = compare_translations(reference, translations)
            
            # Return JSON response
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error in compare translations API: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/translations")
    def list_translations():
        """API endpoint for listing available translations."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT translation_source FROM bible.verse_embeddings ORDER BY translation_source")
            translations = [row['translation_source'] for row in cursor.fetchall()]
            conn.close()
            
            return jsonify({
                "translations": translations
            })
        except Exception as e:
            logger.error(f"Error listing translations: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "ok"})

    @app.route('/ping', methods=['GET'])
    def ping():
        logger.info("/ping called")
        return jsonify({"status": "ok"})

    # Run the application
    port = int(os.getenv("VECTOR_SEARCH_DEMO_PORT", 5150))
    debug = '--debug' in sys.argv
    app.run(debug=debug, port=port) 