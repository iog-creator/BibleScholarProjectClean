#!/usr/bin/env python3
"""
Check database schema to see what tables exist
"""
import psycopg
from psycopg.rows import dict_row

def check_database_schema():
    """Check what tables exist in the database"""
    try:
        conn_str = "postgresql://postgres:password@127.0.0.1:5432/bible_db"
        conn = psycopg.connect(conn_str, row_factory=dict_row)
        
        print("🔍 Checking Database Schema")
        print("=" * 50)
        
        with conn.cursor() as cursor:
            # Get all tables
            cursor.execute("""
                SELECT table_name, table_type
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            
            tables = cursor.fetchall()
            
            print(f"\n📊 Found {len(tables)} tables:")
            for table in tables:
                print(f"  • {table['table_name']} ({table['table_type']})")
            
            # Check for Hebrew/Greek word tables specifically
            hebrew_tables = [t for t in tables if 'hebrew' in t['table_name'].lower()]
            greek_tables = [t for t in tables if 'greek' in t['table_name'].lower()]
            
            print(f"\n🔤 Hebrew-related tables: {len(hebrew_tables)}")
            for table in hebrew_tables:
                print(f"  • {table['table_name']}")
            
            print(f"\n🔤 Greek-related tables: {len(greek_tables)}")
            for table in greek_tables:
                print(f"  • {table['table_name']}")
            
            # Check verses table
            if any(t['table_name'] == 'verses' for t in tables):
                cursor.execute("SELECT COUNT(*) as count FROM verses LIMIT 1")
                verse_count = cursor.fetchone()['count']
                print(f"\n📖 Verses table: {verse_count:,} verses")
            
        conn.close()
        print("\n✅ Database schema check complete!")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n💡 Possible solutions:")
        print("  1. Start PostgreSQL server")
        print("  2. Create bible_db database")
        print("  3. Run ETL pipeline to populate tables")

if __name__ == "__main__":
    check_database_schema() 