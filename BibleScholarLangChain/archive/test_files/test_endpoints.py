import requests
import json
from colorama import Fore, init
import time
import sys
import os
from dotenv import load_dotenv

# Initialize colorama for colored output
init(autoreset=True)
load_dotenv()

# Base URL for API
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000')

def test_endpoint(url, method='GET', params=None, data=None, expected_status=200):
    """Test an API endpoint and return success/failure status"""
    try:
        print(Fore.CYAN + f"Testing {method} {url}...")
        
        if method.upper() == 'GET':
            response = requests.get(url, params=params, timeout=10)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, timeout=10)
        else:
            print(Fore.RED + f"Unsupported method: {method}")
            return False
            
        if response.status_code == expected_status:
            print(Fore.GREEN + f"✓ {method} {url} - Success ({response.status_code})")
            return True
        else:
            print(Fore.RED + f"✗ {method} {url} - Failed ({response.status_code})")
            print(Fore.YELLOW + f"Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(Fore.RED + f"✗ {method} {url} - Error: {e}")
        return False

def main():
    """Run all endpoint tests"""
    success_count = 0
    failure_count = 0
    
    print(Fore.CYAN + "=" * 50)
    print(Fore.CYAN + "Testing BibleScholarLangChain API Endpoints")
    print(Fore.CYAN + "=" * 50)
    
    # Health checks
    endpoints = [
        # Core API health checks
        (f"{API_BASE_URL}/health", 'GET', None, None),
        (f"{API_BASE_URL}/api/vector_search/health", 'GET', None, None),
        (f"{API_BASE_URL}/api/lexicon/health", 'GET', None, None),
        (f"{API_BASE_URL}/api/search/health", 'GET', None, None),
        (f"{API_BASE_URL}/api/cross_language/health", 'GET', None, None),
        
        # Functional endpoints
        (f"{API_BASE_URL}/api/lexicon/search", 'GET', {'strongs_id': 'H430'}, None),
        (f"{API_BASE_URL}/api/search", 'GET', {'q': 'faith', 'type': 'verse'}, None),
        (f"{API_BASE_URL}/api/vector_search/vector-search", 'GET', {'q': 'love', 'translation': 'KJV'}, None),
        (f"{API_BASE_URL}/api/cross_language/terms", 'GET', {'limit': 5}, None)
    ]
    
    # Test each endpoint
    for url, method, params, data in endpoints:
        result = test_endpoint(url, method, params, data)
        if result:
            success_count += 1
        else:
            failure_count += 1
        # Small delay to avoid overwhelming the server
        time.sleep(0.5)
    
    # Summary
    print(Fore.CYAN + "=" * 50)
    print(Fore.GREEN + f"Successful tests: {success_count}")
    print(Fore.RED + f"Failed tests: {failure_count}")
    print(Fore.CYAN + "=" * 50)
    
    return 0 if failure_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main()) 