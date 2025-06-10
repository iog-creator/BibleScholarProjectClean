#!/usr/bin/env python3
"""
Simple script to test server status for BibleScholarLangChain project
"""

import requests
import sys

def test_server_status():
    """Test the status of both API and Web UI servers"""
    print("Testing server connections...")
    
    # Test API Server
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        print(f"API Server (port 5000): ✅ RUNNING - {response.json()}")
    except requests.exceptions.ConnectionError:
        print("API Server (port 5000): ❌ NOT RUNNING - Connection refused")
    except requests.exceptions.Timeout:
        print("API Server (port 5000): ⚠️  TIMEOUT - Server not responding")
    except Exception as e:
        print(f"API Server (port 5000): ❌ ERROR - {str(e)}")
    
    # Test Web UI Server
    try:
        response = requests.get('http://localhost:5002/health', timeout=5)
        print(f"Web UI Server (port 5002): ✅ RUNNING - {response.json()}")
    except requests.exceptions.ConnectionError:
        print("Web UI Server (port 5002): ❌ NOT RUNNING - Connection refused")
    except requests.exceptions.Timeout:
        print("Web UI Server (port 5002): ⚠️  TIMEOUT - Server not responding")
    except Exception as e:
        print(f"Web UI Server (port 5002): ❌ ERROR - {str(e)}")
    
    # Test LM Studio
    try:
        response = requests.get('http://localhost:1234/v1/models', timeout=5)
        print(f"LM Studio (port 1234): ✅ RUNNING - {len(response.json().get('data', []))} models available")
    except requests.exceptions.ConnectionError:
        print("LM Studio (port 1234): ❌ NOT RUNNING - Connection refused")
    except requests.exceptions.Timeout:
        print("LM Studio (port 1234): ⚠️  TIMEOUT - Server not responding")
    except Exception as e:
        print(f"LM Studio (port 1234): ❌ ERROR - {str(e)}")

if __name__ == "__main__":
    test_server_status() 