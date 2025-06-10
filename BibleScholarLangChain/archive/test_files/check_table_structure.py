#!/usr/bin/env python3
"""
Check the structure of bible tables
"""

from src.database.secure_connection import get_secure_connection

def check_table_structure():
    """Check the structure of bible tables"""
    
    try:
        with get_secure_connection() as conn:
            with conn.cursor() as cursor:
                # Check verses table structure
                print("=== BIBLE.VERSES TABLE STRUCTURE ===")
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_schema = 'bible' AND table_name = 'verses'
                    ORDER BY ordinal_position
                """)
                
                columns = cursor.fetchall()
                if columns:
                    for col in columns:
                        print(f"  {col['column_name']} ({col['data_type']}) - {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}")
                else:
                    print("  No columns found or table doesn't exist")
                
                # Sample data from verses table
                print("\n=== SAMPLE DATA FROM BIBLE.VERSES ===")
                cursor.execute("SELECT * FROM bible.verses LIMIT 3")
                sample_verses = cursor.fetchall()
                
                if sample_verses:
                    for i, verse in enumerate(sample_verses, 1):
                        print(f"  Sample {i}: {dict(verse)}")
                else:
                    print("  No data found in verses table")
                
                # Check verse_embeddings table structure
                print("\n=== BIBLE.VERSE_EMBEDDINGS TABLE STRUCTURE ===")
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_schema = 'bible' AND table_name = 'verse_embeddings'
                    ORDER BY ordinal_position
                """)
                
                embedding_columns = cursor.fetchall()
                if embedding_columns:
                    for col in embedding_columns:
                        print(f"  {col['column_name']} ({col['data_type']}) - {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}")
                else:
                    print("  No columns found or table doesn't exist")
                
                # Check all tables in bible schema
                print("\n=== ALL TABLES IN BIBLE SCHEMA ===")
                cursor.execute("""
                    SELECT table_name, 
                           (SELECT COUNT(*) FROM information_schema.columns 
                            WHERE table_schema = 'bible' AND table_name = t.table_name) as column_count
                    FROM information_schema.tables t
                    WHERE table_schema = 'bible'
                    ORDER BY table_name
                """)
                
                tables = cursor.fetchall()
                if tables:
                    for table in tables:
                        print(f"  {table['table_name']} ({table['column_count']} columns)")
                else:
                    print("  No tables found in bible schema")
                
    except Exception as e:
        print(f"Error checking table structure: {e}")

if __name__ == "__main__":
    check_table_structure() 