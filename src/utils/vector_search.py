"""
Vector search utilities for Bible verses.

This module provides functions for searching Bible verses using
semantic similarity with vector embeddings.
"""

import os
import json
import logging
import numpy as np
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from database.connection import get_db_connection
from src.database.secure_connection import get_secure_connection
from src.config.loader import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/vector_search.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def get_embedding(text: str) -> Optional[List[float]]:
    """
    Get embedding vector for a text string using the LM Studio API.
    
    Args:
        text: The text to embed
        
    Returns:
        List of floats representing the embedding vector or None if failed
    """
    try:
        import requests
        config = get_config()
        lm_studio_embeddings_url = config.api.lm_studio_url
        model_name = config.vector_search.embedding_model
        headers = {"Content-Type": "application/json"}
        data = {"model": model_name, "input": text}
        print(f"Teaching Mode: Sending embedding request to {lm_studio_embeddings_url} with model {model_name}")
        try:
            response = requests.post(lm_studio_embeddings_url, headers=headers, json=data, timeout=10)
        except requests.Timeout:
            print("Teaching Mode: LM Studio embedding request timed out after 10 seconds.")
            return None
        except Exception as e:
            print(f"Teaching Mode: Error calling LM Studio for embedding: {e}")
            return None
        print(f"Teaching Mode: Received embedding response with status {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if "data" in result and len(result["data"]) > 0:
                return result["data"][0]["embedding"]
            else:
                logger.error(f"No embedding data in response: {result}")
        else:
            logger.error(f"Error from LM Studio API: {response.status_code}, {response.text}")
        return None
    except Exception as e:
        logger.error(f"Error getting embedding: {e}")
        return None

def log_available_translations():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT translation_source, COUNT(*) FROM bible.verse_embeddings GROUP BY translation_source;")
        rows = cursor.fetchall()
        logger.info(f"Available translations and counts in bible.verse_embeddings: {rows}")
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Error logging available translations: {e}")

def search_verses_by_semantic_similarity(
    query: str, 
    translation: str = "KJV", 
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Search for Bible verses semantically related to the query.
    
    Args:
        query: The search query
        translation: Bible translation to search (default: KJV)
        limit: Maximum number of results to return
        
    Returns:
        List of verse dictionaries with similarity scores
    """
    try:
        log_available_translations()
        # Get embedding for the query
        embedding = get_embedding(query)
        logger.info(f"Semantic search embedding for query '{query}': {embedding}")
        logger.info(f"Translation used: {translation}")
        if not embedding:
            logger.error("Failed to get embedding for query")
            return []
        
        # Convert embedding to string format for PostgreSQL
        embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"
        
        # Connect to the database
        try:
            conn = get_db_connection()
        except Exception as e:
            logger.warning(f"Failed to connect with get_db_connection: {e}")
            try:
                conn = get_secure_connection(mode='read')
            except Exception as e:
                logger.error(f"Failed to connect with secure_connection: {e}")
                return []
        
        cursor = conn.cursor()
        
        # Execute the search query - Fixed to match the schema from the cursor rule
        search_query = """
        SELECT v.verse_id as verse_id, ve.book_name, ve.chapter_num, ve.verse_num, 
               v.text as text, ve.translation_source,
               1 - (ve.embedding <=> %s::vector) as similarity
        FROM bible.verse_embeddings ve
        JOIN bible.verses v ON v.verse_id = ve.verse_id
        WHERE ve.translation_source = %s
        ORDER BY ve.embedding <=> %s::vector
        LIMIT %s
        """
        
        try:
            cursor.execute(search_query, (embedding_str, translation, embedding_str, limit))
            results = cursor.fetchall()
        except Exception as e:
            logger.error(f"Error in semantic search SQL: {e}")
            conn.rollback()
            cursor.close()
            conn.close()
            return []
        
        # Close the connection
        cursor.close()
        conn.close()
        
        # Convert to list of dictionaries
        verse_results = []
        for row in results:
            # Handle different row types (dict or tuple)
            if hasattr(row, 'keys'):
                verse_dict = dict(row)
            else:
                columns = ['verse_id', 'book_name', 'chapter_num', 'verse_num', 
                          'text', 'translation_source', 'similarity']
                verse_dict = dict(zip(columns, row))
            
            # Ensure similarity is a float
            if 'similarity' in verse_dict:
                verse_dict['similarity'] = float(verse_dict['similarity'])
                
            verse_results.append(verse_dict)
        
        logger.info(f"Semantic search returned {len(verse_results)} results.")
        return verse_results
    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        return []

def get_verse_by_reference(
    book_name: str,
    chapter_num: int,
    verse_num: int,
    translation: str = "KJV"
) -> Optional[Dict[str, Any]]:
    """
    Get a specific verse by reference.
    
    Args:
        book_name: Name of the Bible book
        chapter_num: Chapter number
        verse_num: Verse number
        translation: Bible translation
        
    Returns:
        Verse dictionary or None if not found
    """
    try:
        # Connect to the database
        try:
            conn = get_db_connection()
        except Exception as e:
            logger.warning(f"Failed to connect with get_db_connection: {e}")
            try:
                conn = get_secure_connection(mode='read')
            except Exception as e:
                logger.error(f"Failed to connect with secure_connection: {e}")
                return None
        
        cursor = conn.cursor()
        
        # Execute the query
        query = """
        SELECT v.verse_id as verse_id, b.name AS book_name, v.chapter_num, v.verse_num,
               v.text as verse_text, v.translation_source
        FROM bible.verses v
        JOIN bible.books b ON v.book_name = b.name
        WHERE b.name = %s
        AND v.chapter_num = %s
        AND v.verse_num = %s
        AND v.translation_source = %s
        """
        
        cursor.execute(query, (book_name, chapter_num, verse_num, translation))
        result = cursor.fetchone()
        
        # Close the connection
        cursor.close()
        conn.close()
        
        if result:
            # Convert to dictionary
            columns = ['verse_id', 'book_name', 'chapter_num', 'verse_num', 
                       'verse_text', 'translation_source']
            return dict(zip(columns, result))
        
        return None
    except Exception as e:
        logger.error(f"Error getting verse by reference: {e}")
        return None

if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Semantic search for Bible verses.")
    parser.add_argument('--query', required=True, help='Search query')
    parser.add_argument('--translation', default='KJV', help='Bible translation (default: KJV)')
    parser.add_argument('--limit', type=int, default=10, help='Number of results to return (default: 10)')
    args = parser.parse_args()
    results = search_verses_by_semantic_similarity(args.query, args.translation, args.limit)
    print(json.dumps(results, indent=2, ensure_ascii=False)) 