#!/usr/bin/env python3
"""
Test script for enhanced Contextual Insights API
Tests the comprehensive JSON output for second AI agent semantic translation

Based on grokhelp.md instructions to test:
- "John 1:1" (no translation preference, with OT cross-references)
- "beginning" (general query)
- "What is the Word?" (broader question)
"""

import json
import sys
import os
import time
from colorama import Fore, Style, init

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(__file__))

init(autoreset=True)

def test_contextual_insights_enhanced():
    """Test the enhanced contextual insights API"""
    print(f"{Fore.CYAN}🔍 Testing Enhanced Contextual Insights API")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    # Test queries as specified in grokhelp.md
    test_queries = [
        {
            "query": "John 1:1",
            "description": "Specific verse with cross-references to Old Testament",
            "expected_features": ["cross_references", "original_language_notes", "proper_names", "translation_variants"]
        },
        {
            "query": "beginning",
            "description": "General keyword query for semantic search",
            "expected_features": ["semantic_matches", "cross_references", "theological_terms"]
        },
        {
            "query": "What is the Word?",
            "description": "Broader theological question",
            "expected_features": ["theological_terms", "semantic_matches", "original_language_notes"]
        }
    ]
    
    # Test with direct API call
    try:
        from mcp_tools import quick_contextual_insights
        
        for i, test_case in enumerate(test_queries, 1):
            print(f"\n{Fore.YELLOW}Test {i}: {test_case['description']}")
            print(f"{Fore.YELLOW}Query: '{test_case['query']}'{Style.RESET_ALL}")
            
            start_time = time.time()
            result = quick_contextual_insights(test_case['query'])
            elapsed = time.time() - start_time
            
            if 'error' in result:
                print(f"{Fore.RED}❌ Error: {result['error']}")
                if 'suggestion' in result:
                    print(f"{Fore.YELLOW}💡 Suggestion: {result['suggestion']}")
                continue
            
            # Validate JSON structure
            print(f"{Fore.GREEN}✅ Response received in {elapsed:.1f}s")
            
            # Check for required structure
            required_fields = ['input', 'insights', 'processing_time_seconds']
            missing_fields = [field for field in required_fields if field not in result]
            
            if missing_fields:
                print(f"{Fore.RED}❌ Missing required fields: {missing_fields}")
                continue
            
            # Validate input section
            input_section = result.get('input', {})
            if 'reference' not in input_section or 'type' not in input_section:
                print(f"{Fore.RED}❌ Invalid input section structure")
                continue
            
            print(f"{Fore.GREEN}✅ Input section valid:")
            print(f"   Reference: {input_section['reference']}")
            print(f"   Type: {input_section['type']}")
            
            # Validate insights section
            insights = result.get('insights', {})
            expected_insight_fields = [
                'summary', 'theological_terms', 'cross_references', 
                'original_language_notes', 'translation_variants',
                'lexical_data', 'semantic_matches', 'related_entities'
            ]
            
            present_fields = [field for field in expected_insight_fields if field in insights and insights[field]]
            print(f"{Fore.GREEN}✅ Insights fields present: {len(present_fields)}/{len(expected_insight_fields)}")
            print(f"   Fields: {', '.join(present_fields)}")
            
            # Check specific expected features for this query
            feature_results = []
            for feature in test_case['expected_features']:
                if feature in insights and insights[feature]:
                    if isinstance(insights[feature], list) and len(insights[feature]) > 0:
                        feature_results.append(f"✅ {feature}: {len(insights[feature])} items")
                    elif isinstance(insights[feature], dict) and insights[feature]:
                        feature_results.append(f"✅ {feature}: present")
                    elif isinstance(insights[feature], str) and insights[feature].strip():
                        feature_results.append(f"✅ {feature}: present")
                    else:
                        feature_results.append(f"⚠️ {feature}: empty")
                else:
                    feature_results.append(f"❌ {feature}: missing")
            
            print(f"{Fore.CYAN}Feature validation:")
            for result_line in feature_results:
                print(f"   {result_line}")
            
            # Check for Old Testament cross-references (specifically for John 1:1)
            if test_case['query'] == "John 1:1":
                cross_refs = insights.get('cross_references', [])
                ot_refs = [ref for ref in cross_refs if any(book in ref.get('reference', '') for book in ['Gen', 'Pro', 'Psa', 'Isa'])]
                if ot_refs:
                    print(f"{Fore.GREEN}✅ Old Testament cross-references found: {len(ot_refs)}")
                    for ref in ot_refs[:3]:  # Show first 3
                        print(f"   • {ref.get('reference', 'N/A')}: {ref.get('reason', 'Related')}")
                else:
                    print(f"{Fore.YELLOW}⚠️ No Old Testament cross-references found")
            
            # Check for Greek/Hebrew original language data
            orig_lang_notes = insights.get('original_language_notes', [])
            greek_notes = [n for n in orig_lang_notes if n.get('language') == 'Greek']
            hebrew_notes = [n for n in orig_lang_notes if n.get('language') == 'Hebrew']
            
            if greek_notes or hebrew_notes:
                print(f"{Fore.GREEN}✅ Original language data:")
                if greek_notes:
                    print(f"   Greek words: {len(greek_notes)}")
                if hebrew_notes:
                    print(f"   Hebrew words: {len(hebrew_notes)}")
            else:
                print(f"{Fore.YELLOW}⚠️ No original language data found")
            
            # Show sample data for verification
            print(f"{Fore.CYAN}Sample data preview:")
            if insights.get('summary'):
                print(f"   Summary: {insights['summary'][:100]}...")
            
            if insights.get('theological_terms'):
                terms = list(insights['theological_terms'].keys())[:3]
                print(f"   Theological terms: {', '.join(terms)}")
            
            print(f"   Processing time: {result.get('processing_time_seconds', 0)}s")
            
            # Save detailed result for manual inspection
            output_file = f"test_result_{test_case['query'].replace(' ', '_').replace('?', '').replace(':', '_')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"{Fore.BLUE}📄 Detailed result saved to: {output_file}")
            
            print(f"{Fore.CYAN}{'-'*60}")
        
        print(f"\n{Fore.GREEN}🎉 Enhanced Contextual Insights API testing complete!")
        print(f"{Fore.YELLOW}💡 Check the generated JSON files for detailed analysis results")
        
    except ImportError as e:
        print(f"{Fore.RED}❌ Import error: {e}")
        print(f"{Fore.YELLOW}💡 Make sure MCP tools are properly set up")
    except Exception as e:
        print(f"{Fore.RED}❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

def test_api_server_status():
    """Check if the API server is running"""
    try:
        import requests
        response = requests.get("http://localhost:5000/api/contextual_insights/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"{Fore.GREEN}✅ API Server is running")
            print(f"   Status: {health_data.get('status', 'Unknown')}")
            print(f"   Server: {health_data.get('server', 'Unknown')}")
            return True
        else:
            print(f"{Fore.RED}❌ API Server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"{Fore.RED}❌ API Server is not running on port 5000")
        print(f"{Fore.YELLOW}💡 Start the server with: python BibleScholarLangChain/src/api/api_app.py")
        return False
    except Exception as e:
        print(f"{Fore.RED}❌ Error checking API server: {e}")
        return False

if __name__ == "__main__":
    print(f"{Fore.MAGENTA}🧪 Enhanced Contextual Insights API Test Suite")
    print(f"{Fore.MAGENTA}Testing comprehensive JSON output for second AI agent")
    print(f"{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}\n")
    
    # Check API server status first
    if test_api_server_status():
        print()
        test_contextual_insights_enhanced()
    else:
        print(f"\n{Fore.RED}Cannot proceed with tests - API server is not accessible")
        sys.exit(1) 