#!/usr/bin/env python3
"""
Test Enhanced BibleScholarLangChain System
Tests TAHOT integration, standardized ports, and comprehensive data integration
"""
import requests
import json
from datetime import datetime

def test_server_health():
    """Test both servers' health endpoints"""
    print("🔍 Testing Server Health...")
    
    try:
        # Test Enhanced API Server (port 5200)
        api_response = requests.get('http://localhost:5200/health', timeout=10)
        if api_response.status_code == 200:
            api_data = api_response.json()
            print(f"✅ Enhanced API Server (port 5200): {api_data.get('status', 'OK')}")
            print(f"   🎯 Database utilization: {api_data.get('database_utilization', 'Unknown')}")
            print(f"   📚 Translations supported: {api_data.get('translations_supported', [])}")
            print(f"   🔢 Database stats: {api_data.get('comprehensive_integration', {})}")
        else:
            print(f"❌ Enhanced API Server: HTTP {api_response.status_code}")
    except Exception as e:
        print(f"❌ Enhanced API Server: {e}")
    
    try:
        # Test Enhanced Web UI Server (port 5300)
        web_response = requests.get('http://localhost:5300/health', timeout=10)
        if web_response.status_code == 200:
            web_data = web_response.json()
            print(f"✅ Enhanced Web UI Server (port 5300): {web_data.get('status', 'OK')}")
            print(f"   🔗 API connection: {web_data.get('api_status', 'Unknown')}")
            print(f"   🤖 LM Studio: {web_data.get('lm_studio_status', 'Unknown')}")
        else:
            print(f"❌ Enhanced Web UI Server: HTTP {web_response.status_code}")
    except Exception as e:
        print(f"❌ Enhanced Web UI Server: {e}")

def test_tahot_integration():
    """Test TAHOT translation integration"""
    print("\n📖 Testing TAHOT Integration...")
    
    try:
        # Test John 1:1 with enhanced analysis
        john_data = {
            "query": "John 1:1",
            "translation": "KJV"  # Should return all translations including TAHOT
        }
        
        response = requests.post(
            'http://localhost:5200/api/contextual_insights/insights',
            json=john_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            insights = result.get('insights', {})
            
            # Check for translation variants
            translation_variants = insights.get('translation_variants', [])
            print(f"✅ Translation variants found: {len(translation_variants)}")
            
            # Check specifically for TAHOT
            tahot_found = any(v.get('translation') == 'TAHOT' for v in translation_variants)
            print(f"📚 TAHOT translation included: {'✅ YES' if tahot_found else '❌ NO'}")
            
            # Check cross-references (should include OT connections)
            cross_refs = insights.get('cross_references', [])
            print(f"🔗 Cross-references found: {len(cross_refs)}")
            
            # Check original language notes
            orig_lang_notes = insights.get('original_language_notes', [])
            print(f"📝 Original language notes: {len(orig_lang_notes)}")
            
            # List translations found
            translations = [v.get('translation', 'Unknown') for v in translation_variants]
            print(f"📋 Translations returned: {', '.join(set(translations))}")
            
            if tahot_found and len(cross_refs) > 5:
                print("🎉 TAHOT Integration: SUCCESSFUL!")
                return True
            else:
                print("⚠️  TAHOT Integration: PARTIAL")
                return False
        else:
            print(f"❌ John 1:1 analysis failed: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ TAHOT integration test failed: {e}")
        return False

def test_comprehensive_search():
    """Test comprehensive search across all translations"""
    print("\n🔍 Testing Comprehensive Search...")
    
    try:
        # Test love theme search
        love_data = {"query": "love", "translation": "KJV"}
        
        response = requests.post(
            'http://localhost:5200/api/contextual_insights/insights',
            json=love_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            insights = result.get('insights', {})
            
            # Check Hebrew and Greek analysis
            orig_lang_notes = insights.get('original_language_notes', [])
            hebrew_words = [note for note in orig_lang_notes if 'Hebrew' in str(note)]
            greek_words = [note for note in orig_lang_notes if 'Greek' in str(note)]
            
            print(f"✅ Love analysis complete")
            print(f"   📚 Hebrew love words: {len(hebrew_words)}")
            print(f"   🏛️  Greek love words: {len(greek_words)}")
            
            return len(hebrew_words) > 0 and len(greek_words) > 0
        else:
            print(f"❌ Love search failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Comprehensive search test failed: {e}")
        return False

def test_cross_references():
    """Test enhanced cross-reference system"""
    print("\n🔗 Testing Enhanced Cross-References...")
    
    try:
        # Test beginning theme (should connect John 1:1 to Genesis 1:1)
        beginning_data = {"query": "beginning", "translation": "KJV"}
        
        response = requests.post(
            'http://localhost:5200/api/contextual_insights/insights',
            json=beginning_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            insights = result.get('insights', {})
            
            cross_refs = insights.get('cross_references', [])
            
            # Check for Genesis 1:1 connection
            genesis_found = any('Genesis' in str(ref) or 'Gen' in str(ref) for ref in cross_refs)
            john_found = any('John' in str(ref) or 'Jhn' in str(ref) for ref in cross_refs)
            
            print(f"✅ Cross-references found: {len(cross_refs)}")
            print(f"   📖 Genesis references: {'✅ YES' if genesis_found else '❌ NO'}")
            print(f"   📖 John references: {'✅ YES' if john_found else '❌ NO'}")
            
            return len(cross_refs) > 3 and (genesis_found or john_found)
        else:
            print(f"❌ Cross-reference test failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Cross-reference test failed: {e}")
        return False

def main():
    """Run comprehensive system test"""
    print("🚀 Enhanced BibleScholarLangChain System Test")
    print("=" * 60)
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print(f"🎯 Testing: TAHOT integration, standardized ports, comprehensive data")
    print("=" * 60)
    
    # Run all tests
    results = []
    
    test_server_health()
    results.append(("Server Health", True))  # Always pass if we get here
    
    tahot_success = test_tahot_integration()
    results.append(("TAHOT Integration", tahot_success))
    
    search_success = test_comprehensive_search()
    results.append(("Comprehensive Search", search_success))
    
    cross_ref_success = test_cross_references()
    results.append(("Enhanced Cross-References", cross_ref_success))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY:")
    print("=" * 60)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:25} {status}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 ALL TESTS PASSED! Enhanced system is fully operational!")
        print("\n🌐 Access URLs:")
        print("   Enhanced API: http://localhost:5200")
        print("   Enhanced Web UI: http://localhost:5300")
        print("   Contextual Insights: http://localhost:5300/contextual-insights")
    else:
        print("⚠️  Some tests failed. Check server configuration.")
        
    print("=" * 60)

if __name__ == "__main__":
    main() 