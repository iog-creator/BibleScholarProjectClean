#!/usr/bin/env python3
import requests
import json

def test_comprehensive_api():
    try:
        response = requests.post('http://localhost:5000/api/contextual_insights/insights', 
                                json={'query': 'love'}, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            print("🎉 COMPREHENSIVE SEARCH SUCCESS!")
            print(f"Strong's entries: {data['data_sources_used']['strongs_entries']}")
            print(f"Verses found: {data['data_sources_used']['verses_found']}")
            print(f"Semantic matches: {data['data_sources_used']['semantic_matches']}")
            print(f"Cross-references: {data['data_sources_used']['cross_references']}")
            print(f"Morphological entries: {data['data_sources_used']['morphological_entries']}")
            
            if data['raw_data']['strongs_sample']:
                sample = data['raw_data']['strongs_sample'][0]
                print(f"Sample Strong's: {sample['strongs_id']} - {sample['word_text']} ({sample['language']})")
                print(f"Definition: {sample['definition'][:100]}...")
            else:
                print("No Strong's samples found")
                
            print(f"\nAI Insights (first 200 chars): {data['insights'][:200]}...")
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_comprehensive_api() 