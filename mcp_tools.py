"""
Helper module to access Bible Scholar MCP functionality directly from Python.
Re-exports all quick functions and provides convenient aliases.
Now includes automatic operation logging for AI development tracking.

Copyright (c) 2025 BibleScholarLangChain Project

Licensed under the BibleScholarLangChain Personal Biblical Use License.
This software is free for personal biblical study, research, and educational use.
Commercial use requires written permission and payment of licensing fees.
See LICENSE file for full terms.
"""

from mcp_universal_operations import (
    quick_database_check as _quick_database_check,
    quick_server_status as _quick_server_status,
    quick_hebrew_analysis as _quick_hebrew_analysis,
    quick_greek_analysis as _quick_greek_analysis,
    quick_verse_search as _quick_verse_search,
    quick_lexicon_search as _quick_lexicon_search,
    quick_vector_search as _quick_vector_search,
    quick_start_servers as _quick_start_servers,
    quick_stop_servers as _quick_stop_servers,
    quick_rule_check as _quick_rule_check,
    get_system_instructions as _get_system_instructions,
    get_operation_help as _get_operation_help
)

from mcp_operation_logger import log_mcp_operation

# Wrap all functions with automatic logging
@log_mcp_operation
def quick_database_check():
    """Check database connectivity and basic stats for Hebrew/Greek lexicons"""
    return _quick_database_check()

@log_mcp_operation
def quick_server_status():
    """Check status of all Bible Scholar servers (API, Web UI, LM Studio)"""
    return _quick_server_status()

@log_mcp_operation
def quick_hebrew_analysis(word=None, limit=10):
    """Analyze Hebrew words with morphology and lexicon data"""
    return _quick_hebrew_analysis(word, limit)

@log_mcp_operation
def quick_greek_analysis(word=None, limit=10):
    """Analyze Greek words with morphology and lexicon data"""
    return _quick_greek_analysis(word, limit)

@log_mcp_operation
def quick_verse_search(query, limit=5):
    """Search Bible verses across multiple translations"""
    return _quick_verse_search(query, limit)

@log_mcp_operation
def quick_lexicon_search(term, language="both"):
    """Search Hebrew/Greek lexicon for terms and definitions"""
    return _quick_lexicon_search(term, language)

@log_mcp_operation
def quick_vector_search(query, limit=5):
    """Perform semantic similarity search using vector embeddings"""
    return _quick_vector_search(query, limit)

@log_mcp_operation
def quick_start_servers():
    """Start Bible Scholar API and Web UI servers"""
    return _quick_start_servers()

@log_mcp_operation
def quick_stop_servers():
    """Stop Bible Scholar API and Web UI servers"""
    return _quick_stop_servers()

@log_mcp_operation
def quick_rule_check(rule_type="all"):
    """Check compliance with Bible Scholar project rules"""
    return _quick_rule_check(rule_type)

@log_mcp_operation
def get_system_instructions():
    """Get comprehensive Bible Scholar MCP system guide and instructions"""
    return _get_system_instructions()

@log_mcp_operation
def get_operation_help(operation_name=None):
    """Get help for specific Bible Scholar operations"""
    return _get_operation_help(operation_name)

# Convenience aliases for shorter names (also logged)
@log_mcp_operation
def db_check():
    """Alias for quick_database_check()"""
    return _quick_database_check()

@log_mcp_operation
def server_status():
    """Alias for quick_server_status()"""
    return _quick_server_status()

@log_mcp_operation
def search_verses(query, limit=5):
    """Alias for quick_verse_search()"""
    return _quick_verse_search(query, limit)

@log_mcp_operation
def hebrew_search(word=None, limit=10):
    """Alias for quick_hebrew_analysis()"""
    return _quick_hebrew_analysis(word, limit)

@log_mcp_operation
def greek_search(word=None, limit=10):
    """Alias for quick_greek_analysis()"""
    return _quick_greek_analysis(word, limit)

@log_mcp_operation
def help_mcp(operation=None):
    """Alias for get_operation_help()"""
    return _get_operation_help(operation)

@log_mcp_operation
def quick_contextual_insights(query):
    """Get comprehensive contextual insights for a Bible query using all database tables"""
    import requests
    import json
    
    try:
        url = "http://localhost:5200/api/contextual_insights/insights"
        
        # Make request to the enhanced contextual insights API
        response = requests.post(
            url,
            json={"query": query},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"API request failed with status {response.status_code}",
                "response": response.text
            }
    except requests.exceptions.ConnectionError:
        return {
            "error": "Could not connect to contextual insights API. Make sure the API server is running on port 5000.",
            "suggestion": "Run: python BibleScholarLangChain/src/api/api_app.py"
        }
    except Exception as e:
        return {
            "error": f"Error calling contextual insights API: {str(e)}"
        }

def validate_enhanced_system():
    """
    Comprehensive validation of TAHOT integration and standardized ports
    Returns detailed status report of the enhanced BibleScholarLangChain system
    """
    log_mcp_operation("validate_enhanced_system")
    
    validation_results = {
        "timestamp": datetime.now().isoformat(),
        "tahot_integration": {},
        "port_configuration": {},
        "api_functionality": {},
        "overall_status": "unknown"
    }
    
    try:
        # 1. Validate TAHOT Integration
        print("🔍 Validating TAHOT Integration...")
        
        # Test TAHOT in contextual insights
        tahot_test = quick_contextual_insights('John 1:1')
        translations = tahot_test.get('insights', {}).get('translation_variants', [])
        tahot_found = any(t.get('translation') == 'TAHOT' for t in translations)
        
        validation_results["tahot_integration"] = {
            "tahot_in_translations": tahot_found,
            "total_translations": len(translations),
            "translation_list": [t.get('translation') for t in translations],
            "status": "✅ PASS" if tahot_found else "❌ FAIL"
        }
        
        # 2. Validate Standardized Ports
        print("🔌 Validating Standardized Ports...")
        
        port_tests = {}
        
        # Test API Server (port 5200)
        try:
            api_response = requests.get('http://localhost:5200/health', timeout=10)
            port_tests["api_5200"] = {
                "accessible": api_response.status_code == 200,
                "response": api_response.json() if api_response.status_code == 200 else None,
                "status": "✅ LISTENING" if api_response.status_code == 200 else "❌ NOT RESPONDING"
            }
        except Exception as e:
            port_tests["api_5200"] = {
                "accessible": False,
                "error": str(e),
                "status": "❌ CONNECTION FAILED"
            }
        
        # Test Web UI (port 5300)
        try:
            web_response = requests.get('http://localhost:5300/health', timeout=10)
            port_tests["web_5300"] = {
                "accessible": web_response.status_code == 200,
                "response": web_response.json() if web_response.status_code == 200 else None,
                "status": "✅ LISTENING" if web_response.status_code == 200 else "❌ NOT RESPONDING"
            }
        except Exception as e:
            port_tests["web_5300"] = {
                "accessible": False,
                "error": str(e),
                "status": "❌ CONNECTION FAILED"
            }
        
        validation_results["port_configuration"] = port_tests
        
        # 3. Validate API Functionality
        print("🧪 Validating API Functionality...")
        
        api_tests = {}
        
        # Test contextual insights endpoint
        try:
            insights_response = requests.get(
                'http://localhost:5200/api/contextual_insights/insights',
                params={'query': 'John 1:1'},
                timeout=15
            )
            api_tests["contextual_insights"] = {
                "accessible": insights_response.status_code == 200,
                "has_data": bool(insights_response.json().get('insights')) if insights_response.status_code == 200 else False,
                "status": "✅ WORKING" if insights_response.status_code == 200 else "❌ ERROR"
            }
        except Exception as e:
            api_tests["contextual_insights"] = {
                "accessible": False,
                "error": str(e),
                "status": "❌ CONNECTION FAILED"
            }
        
        validation_results["api_functionality"] = api_tests
        
        # 4. Overall System Status
        tahot_ok = validation_results["tahot_integration"]["status"] == "✅ PASS"
        api_ok = port_tests.get("api_5200", {}).get("accessible", False)
        web_ok = port_tests.get("web_5300", {}).get("accessible", False)
        insights_ok = api_tests.get("contextual_insights", {}).get("accessible", False)
        
        all_systems_ok = tahot_ok and api_ok and web_ok and insights_ok
        
        validation_results["overall_status"] = "✅ FULLY OPERATIONAL" if all_systems_ok else "⚠️ ISSUES DETECTED"
        
        # 5. Print Comprehensive Report
        print("\n" + "="*60)
        print("🎯 ENHANCED BIBLESCHOLAR SYSTEM VALIDATION REPORT")
        print("="*60)
        
        print(f"\n📊 OVERALL STATUS: {validation_results['overall_status']}")
        
        print(f"\n🔤 TAHOT Integration: {validation_results['tahot_integration']['status']}")
        if tahot_found:
            print(f"   ✅ TAHOT found in translation variants")
            print(f"   📋 Available translations: {', '.join(validation_results['tahot_integration']['translation_list'])}")
        else:
            print(f"   ❌ TAHOT missing from translation variants")
        
        print(f"\n🔌 Port Configuration:")
        print(f"   API Server (5200): {port_tests.get('api_5200', {}).get('status', 'UNKNOWN')}")
        print(f"   Web UI (5300): {port_tests.get('web_5300', {}).get('status', 'UNKNOWN')}")
        
        print(f"\n🧪 API Functionality:")
        print(f"   Contextual Insights: {api_tests.get('contextual_insights', {}).get('status', 'UNKNOWN')}")
        
        if all_systems_ok:
            print(f"\n🎉 SUCCESS: Enhanced BibleScholarLangChain system is fully operational!")
            print(f"   • TAHOT integration: Working")
            print(f"   • Standardized ports: Active")
            print(f"   • Enhanced APIs: Functional")
            print(f"   • Ready for production use")
        else:
            print(f"\n⚠️  WARNING: System issues detected. Check individual components above.")
        
        print("="*60)
        
        return validation_results
        
    except Exception as e:
        validation_results["error"] = str(e)
        validation_results["overall_status"] = "❌ VALIDATION FAILED"
        print(f"❌ System validation failed: {e}")
        return validation_results

# Add alias for easy access
def system_health_check():
    """Alias for validate_enhanced_system"""
    return validate_enhanced_system()

# Directly importable quick functions
__all__ = [
    'quick_database_check',
    'quick_server_status',
    'quick_hebrew_analysis',
    'quick_greek_analysis',
    'quick_verse_search',
    'quick_lexicon_search',
    'quick_vector_search',
    'quick_contextual_insights',
    'quick_start_servers',
    'quick_stop_servers',
    'quick_rule_check',
    'get_system_instructions',
    'get_operation_help',
    # aliases
    'db_check',
    'server_status',
    'search_verses',
    'hebrew_search',
    'greek_search',
    'help_mcp'
]

# Expose logging functions for manual use
from mcp_operation_logger import (
    get_all_registered_tools,
    get_operation_stats,
    get_recent_successful_operations,
    log_success,
    log_error
)

__all__.extend([
    'get_all_registered_tools',
    'get_operation_stats', 
    'get_recent_successful_operations',
    'log_success',
    'log_error'
])

# Print initialization message
print("[MCP-TOOLS] 🔧 Bible Scholar MCP tools loaded with automatic operation logging")
print("[MCP-TOOLS] 📊 All function calls will be automatically tracked and logged")
print("[MCP-TOOLS] 🎯 Use get_operation_stats() to view usage statistics") 