#!/usr/bin/env python3
import requests
import json

def get_full_response():
    try:
        response = requests.post(
            'http://localhost:5000/api/contextual_insights/insights',
            json={'query': 'love'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print("=== COMPREHENSIVE BIBLE STUDY ANALYSIS ===\n")
            
            print("📊 DATA SOURCES USED:")
            sources = data['data_sources_used']
            print(f"  ✅ Verses found: {sources['verses_found']}")
            print(f"  ✅ Strong's entries: {sources['strongs_entries']}")  
            print(f"  ✅ Morphological entries: {sources['morphological_entries']}")
            print(f"  ✅ Cross-references: {sources['cross_references']}")
            print(f"  ✅ Semantic matches: {sources['semantic_matches']}")
            
            print("\n📚 SAMPLE VERSES:")
            for verse in data['raw_data']['verses_sample'][:3]:
                print(f"  • {verse['book_name']} {verse['chapter_num']}:{verse['verse_num']} ({verse['translation_source']})")
                print(f"    \"{verse['text'][:100]}...\"")
                
            print("\n🔤 SAMPLE STRONG'S ENTRIES:")
            for strong in data['raw_data']['strongs_sample'][:3]:
                print(f"  • {strong['word_text']} ({strong['strongs_id']}): {strong['lemma']}")
                print(f"    Definition: {strong['definition'][:100]}...")
                
            print("\n📝 SAMPLE MORPHOLOGICAL ANALYSIS:")
            for morph in data['raw_data']['morphology_sample'][:3]:
                ref = f"{morph.get('book_name', '')} {morph.get('chapter_num', '')}:{morph.get('verse_num', '')}"
                print(f"  • {morph['word_text']} ({morph['strongs_id']}) [{morph['grammar_code']}]")
                print(f"    {morph['gloss']} - {ref}")
                
            print("\n🤖 AI ANALYSIS:")
            analysis = data.get('analysis', 'No analysis available')
            print(f"  {analysis[:300]}...")
            
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    get_full_response() 