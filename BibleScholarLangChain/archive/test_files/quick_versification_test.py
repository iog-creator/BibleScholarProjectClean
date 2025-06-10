import requests
import json

def quick_versification_test():
    """Quick test to check versification via API without hanging"""
    try:
        print("🔄 Testing versification through API...")
        
        # Test the API that's already running
        response = requests.post(
            'http://localhost:5000/api/contextual_insights/test_comprehensive',
            timeout=10  # Short timeout to avoid hanging
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Response:")
            test_results = data.get('test_results', {})
            for key, value in test_results.items():
                print(f"  {key}: {value}")
                
            # Check if cross-references are 0
            cross_refs = test_results.get('cross_references', 0)
            if cross_refs == 0:
                print("\n❌ ISSUE: Cross-references returning 0")
                print("📝 This confirms versification mappings aren't working in the join")
            else:
                print(f"\n✅ Cross-references working: {cross_refs}")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - API might be busy")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_manual_query():
    """Test with a simple manual database query"""
    try:
        print("\n🔄 Testing simple database count...")
        import psycopg
        
        # Very simple connection test
        with psycopg.connect(
            "host=localhost dbname=bible_db user=postgres password=postgres",
            connect_timeout=5
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM bible.versification_mappings")
                count = cursor.fetchone()[0]
                print(f"✅ Versification mappings count: {count}")
                
                if count > 0:
                    # Quick sample
                    cursor.execute("SELECT source_book, source_chapter, source_verse FROM bible.versification_mappings LIMIT 1")
                    sample = cursor.fetchone()
                    print(f"📄 Sample: {sample}")
                    
                    # Test if any verses match
                    cursor.execute("""
                        SELECT COUNT(*) FROM bible.versification_mappings vm
                        JOIN bible.verses v ON (
                            v.book_name = vm.source_book 
                            AND v.chapter_num::text = vm.source_chapter 
                            AND v.verse_num::text = vm.source_verse
                        ) LIMIT 1
                    """)
                    joins = cursor.fetchone()[0]
                    print(f"🔗 Successful joins: {joins}")
                    
    except Exception as e:
        print(f"❌ Database test failed: {e}")

if __name__ == "__main__":
    quick_versification_test()
    test_manual_query() 