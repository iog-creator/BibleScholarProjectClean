#!/usr/bin/env python3
"""
Test API Registration for BibleScholarLangChain

This test checks if the comprehensive search API is properly registered
in the main Flask application.
"""

import sys
import os
from colorama import Fore, init

init(autoreset=True)

print(f"{Fore.CYAN}🔧 Testing API Registration...")

# Add project root to path
sys.path.append('C:\\Users\\mccoy\\Documents\\Projects\\Projects\\CursorMCPWorkspace')

# Test 1: Import the main API app
print(f"\n{Fore.YELLOW}Test 1: Testing main API app imports...")
try:
    from BibleScholarLangChain.src.api.api_app import app
    print(f"{Fore.GREEN}✅ Main API app imported successfully")
except Exception as e:
    print(f"{Fore.RED}❌ Main API app import failed: {e}")

# Test 2: Check registered blueprints
print(f"\n{Fore.YELLOW}Test 2: Checking registered blueprints...")
try:
    blueprint_names = [bp.name for bp in app.blueprints.values()]
    print(f"{Fore.BLUE}📋 Registered blueprints: {blueprint_names}")
    
    if 'comprehensive_search' in blueprint_names:
        print(f"{Fore.GREEN}✅ Comprehensive search blueprint is registered")
    else:
        print(f"{Fore.RED}❌ Comprehensive search blueprint is NOT registered")
        
except Exception as e:
    print(f"{Fore.RED}❌ Blueprint check failed: {e}")

# Test 3: Check URL rules
print(f"\n{Fore.YELLOW}Test 3: Checking URL rules...")
try:
    comprehensive_urls = []
    for rule in app.url_map.iter_rules():
        if 'comprehensive' in rule.rule:
            comprehensive_urls.append(rule.rule)
    
    print(f"{Fore.BLUE}🔗 Comprehensive search URLs: {comprehensive_urls}")
    
    if comprehensive_urls:
        print(f"{Fore.GREEN}✅ Comprehensive search URLs are registered")
    else:
        print(f"{Fore.RED}❌ No comprehensive search URLs found")
        
except Exception as e:
    print(f"{Fore.RED}❌ URL rules check failed: {e}")

# Test 4: Test the Flask app context
print(f"\n{Fore.YELLOW}Test 4: Testing Flask app context...")
try:
    with app.test_client() as client:
        # Test main endpoint
        response = client.get('/')
        print(f"{Fore.BLUE}📊 Main endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.get_json()
            features = data.get('features', {})
            comprehensive_available = features.get('comprehensive_search', False)
            print(f"{Fore.BLUE}🔍 Comprehensive search available: {comprehensive_available}")
            
            if comprehensive_available:
                print(f"{Fore.GREEN}✅ Comprehensive search is marked as available")
            else:
                print(f"{Fore.RED}❌ Comprehensive search is marked as unavailable")
        
        # Test comprehensive search status
        status_response = client.get('/api/comprehensive/status')
        print(f"{Fore.BLUE}📊 Comprehensive status endpoint: {status_response.status_code}")
        
        if status_response.status_code == 200:
            print(f"{Fore.GREEN}✅ Comprehensive search status endpoint working")
        elif status_response.status_code == 404:
            print(f"{Fore.RED}❌ Comprehensive search status endpoint not found")
        else:
            print(f"{Fore.YELLOW}⚠️ Comprehensive search status endpoint error: {status_response.status_code}")
            
except Exception as e:
    print(f"{Fore.RED}❌ Flask app context test failed: {e}")

print(f"\n{Fore.CYAN}🎯 API Registration Test Summary:")
print(f"{Fore.GREEN}✅ Tests completed") 