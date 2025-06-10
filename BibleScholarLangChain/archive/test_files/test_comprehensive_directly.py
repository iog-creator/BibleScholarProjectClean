import sys
import os
sys.path.append('src')

from api.contextual_insights_api import ComprehensiveBibleAnalyzer

def test_new_methods():
    """Test the new comprehensive data source methods directly"""
    print("Testing new comprehensive data source methods...")
    
    analyzer = ComprehensiveBibleAnalyzer()
    
    # Test morphology code descriptions
    print("\n1. Testing morphology code descriptions...")
    sample_morphology = [
        {'grammar_code': 'Hc/Vqw3ms', 'language': 'Hebrew'},
        {'grammar_code': 'N-NSM', 'language': 'Greek'}
    ]
    morphology_codes = analyzer.get_morphology_code_descriptions(sample_morphology)
    print(f"Found {len(morphology_codes)} morphology code descriptions")
    
    # Test versification mappings
    print("\n2. Testing versification mappings...")
    sample_verse_ids = [130253, 70757]  # Some verse IDs from love search
    versification_mappings = analyzer.get_versification_mappings(sample_verse_ids)
    print(f"Found {len(versification_mappings)} versification mappings")
    
    # Test complete translation analysis
    print("\n3. Testing complete translation analysis...")
    translation_analysis = analyzer.get_complete_translation_analysis("love")
    available_translations = translation_analysis.get('available_translations', [])
    search_results = translation_analysis.get('search_results', [])
    print(f"Found {len(available_translations)} available translations")
    print(f"Found {len(search_results)} translation search results")
    
    if available_translations:
        print("Available translations:")
        for trans in available_translations[:3]:
            print(f"  {trans['translation_source']}: {trans['verse_count']} verses")
    
    if search_results:
        print("Sample search results:")
        for result in search_results[:2]:
            print(f"  {result['translation_source']}: {result['book_name']} {result['chapter_num']}:{result['verse_num']}")

if __name__ == "__main__":
    test_new_methods() 