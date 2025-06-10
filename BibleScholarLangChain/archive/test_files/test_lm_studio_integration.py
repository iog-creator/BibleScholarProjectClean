#!/usr/bin/env python3
"""
Test script to verify LM Studio integration is working end-to-end
"""
import requests
import json
import time

def test_lm_studio_direct():
    """Test LM Studio directly"""
    print("🔍 Testing LM Studio directly...")
    
    try:
        # Test models endpoint
        response = requests.get('http://localhost:1234/v1/models', timeout=5)
        if response.status_code == 200:
            models = response.json()
            print(f"✅ LM Studio models: {len(models['data'])} available")
        else:
            print(f"❌ LM Studio models failed: {response.status_code}")
            return False
            
        # Test embeddings endpoint
        response = requests.post(
            'http://localhost:1234/v1/embeddings',
            json={"input": "test", "model": "text-embedding-bge-m3"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            embedding_size = len(data['data'][0]['embedding'])
            print(f"✅ LM Studio embeddings: {embedding_size} dimensions")
        else:
            print(f"❌ LM Studio embeddings failed: {response.status_code}")
            return False
            
        # Test chat completions
        response = requests.post(
            'http://localhost:1234/v1/chat/completions',
            json={
                "model": "meta-llama-3.1-8b-instruct",
                "messages": [{"role": "user", "content": "Say 'LM Studio is working'"}],
                "max_tokens": 10
            },
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            reply = data['choices'][0]['message']['content']
            print(f"✅ LM Studio chat: {reply}")
        else:
            print(f"❌ LM Studio chat failed: {response.status_code}")
            return False
            
        return True
    except Exception as e:
        print(f"❌ LM Studio direct test failed: {e}")
        return False

def test_api_server():
    """Test our API server LM Studio integration"""
    print("\n🔍 Testing API server LM Studio integration...")
    
    try:
        # Test the test endpoint
        response = requests.get('http://localhost:5000/api/contextual_insights/test_lm_studio', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API test endpoint: {data['status']}")
            print(f"   Model: {data['model']}")
            print(f"   Embedding dimensions: {data['embedding_dimensions']}")
        else:
            print(f"❌ API test endpoint failed: {response.status_code}")
            return False
            
        # Test the insights endpoint
        print("\n🧠 Testing insights generation...")
        start_time = time.time()
        
        response = requests.post(
            'http://localhost:5000/api/contextual_insights/insights',
            json={"query": "What does John 3:16 teach us?", "include_verses": False},
            timeout=30
        )
        
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Insights generated in {end_time - start_time:.2f} seconds")
            print(f"   Query: {data['query']}")
            print(f"   Model: {data['model']}")
            print(f"   Insights length: {len(data['insights'])} characters")
            print(f"   Sample: {data['insights'][:100]}...")
        else:
            print(f"❌ Insights endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
        return True
    except Exception as e:
        print(f"❌ API server test failed: {e}")
        return False

def test_web_search():
    """Test web UI search functionality"""
    print("\n🔍 Testing web UI search...")
    
    try:
        response = requests.get('http://localhost:5002/api/search?q=love&type=verse', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search found {data['count']} results in {data['search_time']}s")
            if data['results']:
                first_result = data['results'][0]
                print(f"   First result: {first_result['book']} {first_result['chapter']}:{first_result['verse']}")
        else:
            print(f"❌ Web search failed: {response.status_code}")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Web search test failed: {e}")
        return False

def main():
    print("🚀 Testing BibleScholarLangChain LM Studio Integration")
    print("=" * 60)
    
    # Test LM Studio directly
    if not test_lm_studio_direct():
        print("\n❌ LM Studio is not working properly. Please check LM Studio setup.")
        return
    
    # Test API server
    if not test_api_server():
        print("\n❌ API server LM Studio integration is not working.")
        return
        
    # Test web search
    if not test_web_search():
        print("\n❌ Web UI search is not working.")
        return
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("✅ LM Studio is properly integrated and working")
    print("✅ API server is calling LM Studio successfully")
    print("✅ Web UI search is working")
    print("\n📱 You can now:")
    print("   1. Go to http://localhost:5002/search")
    print("   2. Search for Bible verses")
    print("   3. Click 'Get Insights' on any verse to call LM Studio")
    print("   4. Watch the console for LM Studio API calls")

if __name__ == "__main__":
    main() 