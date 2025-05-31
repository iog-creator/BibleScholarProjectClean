import requests
import json

url = 'http://localhost:5002/api/contextual_insights/insights'
payload = {
    'type': 'verse',
    'reference': 'John 3:16',
    'translation': 'KJV'
}

try:
    resp = requests.post(url, json=payload, timeout=120)
    resp.raise_for_status()
    with open('insights_output.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    print('Output written to insights_output.json')
except Exception as e:
    print(f'Error: {e}') 