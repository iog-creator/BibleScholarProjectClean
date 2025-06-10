#!/usr/bin/env python3
"""Test web server connectivity"""
import requests
import time

def test_web_server():
    print("Testing Web UI Server on port 5002...")
    
    try:
        response = requests.get('http://localhost:5002/health', timeout=10)
        print(f"✅ Web server response: {response.status_code}")
        print(f"✅ Response data: {response.json()}")
        return True
    except requests.exceptions.Timeout:
        print("❌ Web server request timed out")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to web server")
        return False
    except Exception as e:
        print(f"❌ Web server error: {e}")
        return False

def test_api_server():
    print("\nTesting API Server on port 5000...")
    
    try:
        response = requests.get('http://localhost:5000/api/contextual_insights/health', timeout=10)
        print(f"✅ API server response: {response.status_code}")
        print(f"✅ Response data: {response.json()}")
        return True
    except requests.exceptions.Timeout:
        print("❌ API server request timed out")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        return False
    except Exception as e:
        print(f"❌ API server error: {e}")
        return False

def test_search_through_web():
    print("\nTesting search through web UI...")
    
    try:
        response = requests.get('http://localhost:5002/api/search?q=love&type=verse', timeout=15)
        print(f"✅ Search response: {response.status_code}")
        data = response.json()
        print(f"✅ Search results count: {len(data.get('results', []))}")
        return True
    except requests.exceptions.Timeout:
        print("❌ Search request timed out")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect for search")
        return False
    except Exception as e:
        print(f"❌ Search error: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("🔍 Diagnostic Test for BibleScholarLangChain")
    print("=" * 60)
    
    web_ok = test_web_server()
    api_ok = test_api_server()
    
    if web_ok and api_ok:
        print("\n🔍 Testing end-to-end search functionality...")
        search_ok = test_search_through_web()
        
        if search_ok:
            print("\n✅ All tests passed! The system should be working.")
        else:
            print("\n❌ Search functionality is not working properly.")
    else:
        print("\n❌ Basic connectivity issues detected.")
        
    print("\nDone.") 