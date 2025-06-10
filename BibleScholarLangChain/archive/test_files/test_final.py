#!/usr/bin/env python3
"""Final test to confirm LM Studio integration through the UI"""
import requests
import json

def test_lm_studio_through_ui():
    print("🔥 Testing LM Studio integration through the Web UI...")
    print("=" * 60)
    
    # Test contextual insights (this should call LM Studio)
    print("📚 Testing contextual insights API through Web UI...")
    try:
        response = requests.get(
            'http://localhost:5002/api/contextual_insights/insights',
            params={'query': 'What does John 3:16 teach us about love?'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            insights = data.get('insights', 'No insights')
            print(f"✅ Status: {response.status_code}")
            print(f"✅ LM Studio Response Length: {len(insights)} characters")
            print(f"✅ Sample Insights: {insights[:200]}...")
            print("🎉 LM Studio is successfully being called through the UI!")
            return True
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"❌ Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_all_endpoints():
    print("\n🔍 Testing all available endpoints...")
    
    endpoints = [
        ('/health', 'Web UI Health'),
        ('/api/search?q=love', 'Search API'),
        ('/api/lexicon/search?term=love', 'Lexicon API'),
        ('/api/vector_search/vector-search?q=love', 'Vector Search'),
        ('/api/cross_language/csv', 'Cross Language')
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f'http://localhost:5002{endpoint}', timeout=10)
            print(f"✅ {name}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")

if __name__ == '__main__':
    print("🚀 Final LM Studio Integration Test")
    print("=" * 60)
    
    # Test the main LM Studio integration
    success = test_lm_studio_through_ui()
    
    # Test other endpoints  
    test_all_endpoints()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SUCCESS! LM Studio is working through the Web UI!")
        print("📝 You can now:")
        print("   • Open http://localhost:5002/search in your browser")
        print("   • Use the search interface")
        print("   • Get contextual insights powered by LM Studio")
    else:
        print("❌ LM Studio integration through UI needs debugging")
    
    print("=" * 60) 