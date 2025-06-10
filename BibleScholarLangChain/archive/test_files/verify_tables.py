import sys
import os
sys.path.append('src')

def test_direct_query():
    """Direct query test without dependencies"""
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="bible_db", 
            user="postgres",
            password="postgres",
            cursor_factory=RealDictCursor
        )
        
        with conn.cursor() as cursor:
            print("Testing table existence and data:")
            
            # Test if tables exist
            cursor.execute("""
                SELECT table_name, table_schema 
                FROM information_schema.tables 
                WHERE table_name IN ('tahot_verses_staging', 'proper_names')
                AND table_schema = 'bible'
            """)
            tables = cursor.fetchall()
            print(f"Tables found: {[t['table_name'] for t in tables]}")
            
            if tables:
                # Check TAHOT data
                try:
                    cursor.execute("SELECT COUNT(*) as count FROM bible.tahot_verses_staging")
                    tahot_count = cursor.fetchone()['count']
                    print(f"TAHOT verses total: {tahot_count}")
                    
                    if tahot_count > 0:
                        cursor.execute("SELECT book_id, chapter, verse, LEFT(text, 50) as sample FROM bible.tahot_verses_staging LIMIT 3")
                        tahot_samples = cursor.fetchall()
                        print("TAHOT samples:")
                        for sample in tahot_samples:
                            print(f"  {sample['book_id']} {sample['chapter']}:{sample['verse']}: {sample['sample']}")
                except Exception as e:
                    print(f"TAHOT error: {e}")
                
                # Check proper names data
                try:
                    cursor.execute("SELECT COUNT(*) as count FROM bible.proper_names")
                    names_count = cursor.fetchone()['count']
                    print(f"Proper names total: {names_count}")
                    
                    if names_count > 0:
                        cursor.execute("SELECT unified_name, type, LEFT(description, 50) as sample FROM bible.proper_names LIMIT 3")
                        names_samples = cursor.fetchall()
                        print("Proper names samples:")
                        for sample in names_samples:
                            print(f"  {sample['unified_name']} ({sample['type']}): {sample['sample']}")
                except Exception as e:
                    print(f"Proper names error: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"Database connection error: {e}")

if __name__ == "__main__":
    test_direct_query() 