import requests
import json

def test_comprehensive_integration():
    """Test the comprehensive integration and see full error details"""
    try:
        # Test the API
        response = requests.post(
            'http://localhost:5000/api/contextual_insights/insights',
            json={'query': 'love'},
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("🎉 SUCCESS!")
            print(f"Data sources used: {data.get('data_sources_used', {})}")
            
            # Check for all data types
            sources = data.get('data_sources_used', {})
            print(f"✅ Verses: {sources.get('verses_found', 0)}")
            print(f"✅ Strong's entries: {sources.get('strongs_entries', 0)}")
            print(f"✅ Morphological entries: {sources.get('morphological_entries', 0)}")
            print(f"✅ Cross-references: {sources.get('cross_references', 0)}")
            print(f"✅ Semantic matches: {sources.get('semantic_matches', 0)}")
            
            return True
        else:
            print(f"❌ ERROR {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"🚨 Exception: {e}")
        return False

if __name__ == "__main__":
    test_comprehensive_integration() 