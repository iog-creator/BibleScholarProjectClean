import sys
import os
sys.path.append('src')

# Import the get_db_connection function directly from contextual_insights_api
from api.contextual_insights_api import get_db_connection

def check_tables():
    """Check if TAHOT and proper names tables exist and have data"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Check TAHOT verses count
                cursor.execute("SELECT COUNT(*) FROM bible.tahot_verses_staging")
                tahot_count = cursor.fetchone()[0]
                print(f"TAHOT verses total count: {tahot_count}")
                
                # Check proper names count  
                cursor.execute("SELECT COUNT(*) FROM bible.proper_names")
                names_count = cursor.fetchone()[0]
                print(f"Proper names total count: {names_count}")
                
                # Test love search in TAHOT
                cursor.execute("""
                    SELECT COUNT(*) FROM bible.tahot_verses_staging 
                    WHERE text ILIKE %s
                """, ('%love%',))
                tahot_love_count = cursor.fetchone()[0]
                print(f"TAHOT verses with 'love': {tahot_love_count}")
                
                # Test love search in proper names
                cursor.execute("""
                    SELECT COUNT(*) FROM bible.proper_names 
                    WHERE unified_name ILIKE %s 
                    OR description ILIKE %s
                    OR briefest ILIKE %s
                """, ('%love%', '%love%', '%love%'))
                names_love_count = cursor.fetchone()[0]
                print(f"Proper names with 'love': {names_love_count}")
                
    except Exception as e:
        print(f"Error checking tables: {e}")

if __name__ == "__main__":
    check_tables() 