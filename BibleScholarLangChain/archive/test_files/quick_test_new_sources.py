import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database.connection import get_db_connection

def test_tahot_verses(query_text="love", limit=5):
    """Test TAHOT verses staging data"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT book_id, chapter, verse, LEFT(text, 100) as text_sample
                    FROM bible.tahot_verses_staging
                    WHERE text ILIKE %s
                    LIMIT %s
                """, (f'%{query_text}%', limit))
                results = cursor.fetchall()
                print(f"TAHOT verses found: {len(results)}")
                for result in results[:3]:
                    print(f"  {result['book_id']} {result['chapter']}:{result['verse']}: {result['text_sample']}")
                return [dict(row) for row in results]
    except Exception as e:
        print(f"Error getting TAHOT verses: {e}")
        return []

def test_proper_names(query_text="love", limit=5):
    """Test proper names data"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT unified_name, description, type, category, 
                           briefest, brief, short
                    FROM bible.proper_names
                    WHERE unified_name ILIKE %s 
                    OR description ILIKE %s
                    OR briefest ILIKE %s
                    LIMIT %s
                """, (f'%{query_text}%', f'%{query_text}%', f'%{query_text}%', limit))
                results = cursor.fetchall()
                print(f"Proper names found: {len(results)}")
                for result in results[:3]:
                    print(f"  {result['unified_name']} ({result['type']}): {result['description'][:60] if result['description'] else 'N/A'}...")
                return [dict(row) for row in results]
    except Exception as e:
        print(f"Error getting proper names: {e}")
        return []

if __name__ == "__main__":
    print("Testing new data sources:")
    tahot_results = test_tahot_verses()
    proper_names_results = test_proper_names()
    
    print(f"\nSummary:")
    print(f"TAHOT verses: {len(tahot_results)}")
    print(f"Proper names: {len(proper_names_results)}") 