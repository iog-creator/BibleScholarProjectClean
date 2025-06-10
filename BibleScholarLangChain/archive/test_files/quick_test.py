#!/usr/bin/env python3
import requests
import json

def quick_test():
    try:
        print("Testing API endpoint...")
        
        # Test health first
        health_response = requests.get('http://localhost:5000/health', timeout=5)
        print(f"Health: {health_response.status_code}")
        
        # Test insights
        insights_response = requests.post(
            'http://localhost:5000/api/contextual_insights/insights', 
            json={'query': 'love'}, 
            timeout=60
        )
        
        print(f"Insights status: {insights_response.status_code}")
        
        if insights_response.status_code == 200:
            data = insights_response.json()
            print(f"Strong's entries: {data['data_sources_used']['strongs_entries']}")
            print(f"Morphological entries: {data['data_sources_used']['morphological_entries']}")
            print(f"Verses found: {data['data_sources_used']['verses_found']}")
        else:
            print(f"Error response: {insights_response.text}")
            
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    quick_test() 