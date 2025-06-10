#!/usr/bin/env python3
import requests
import json

def check_response_structure():
    try:
        response = requests.post(
            'http://localhost:5000/api/contextual_insights/insights',
            json={'query': 'love'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print("Response keys:", list(data.keys()))
            print("Data sources keys:", list(data['data_sources_used'].keys()))
            
            if 'raw_data' in data:
                print("Raw data keys:", list(data['raw_data'].keys()))
            else:
                print("No 'raw_data' key found")
                
            # Print first few lines of the actual response
            print("\nFirst 500 chars of response:")
            print(json.dumps(data, indent=2)[:500])
            
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    check_response_structure() 