#!/usr/bin/env python3
"""Quick test script to verify servers are working"""
import requests
import json

def test_servers():
    print("Testing BibleScholarLangChain servers...")
    
    # Test API server health
    try:
        r = requests.get('http://localhost:5000/health', timeout=5)
        print(f"API Server (5000): Status {r.status_code}")
        print(f"Response: {r.json()}")
    except Exception as e:
        print(f"API Server (5000): ERROR - {e}")
    
    # Test Web UI server health
    try:
        r = requests.get('http://localhost:5002/health', timeout=5)
        print(f"Web UI Server (5002): Status {r.status_code}")
        print(f"Response: {r.json()}")
    except Exception as e:
        print(f"Web UI Server (5002): ERROR - {e}")
    
    # Test search functionality
    try:
        r = requests.get('http://localhost:5002/api/search?q=faith&type=verse', timeout=10)
        print(f"Search API: Status {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Found {len(data.get('results', []))} results for 'faith'")
            if data.get('results'):
                print(f"First result: {data['results'][0]}")
        else:
            print(f"Search error: {r.text}")
    except Exception as e:
        print(f"Search API: ERROR - {e}")

if __name__ == "__main__":
    test_servers() 