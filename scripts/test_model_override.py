import requests
import json

# Teaching: This script sends a POST request to the Contextual Insights API with a model override.
# You can run it with: python scripts/test_model_override.py

url = "http://localhost:5002/api/contextual_insights/insights"
payload = {
    "type": "verse",  # input type: 'verse', 'topic', or 'text_snippet'
    "reference": "John 1:1",  # the Bible reference
    "translation": "KJV",  # translation (optional, default is KJV)
    "model": "microsoft/phi-4-mini-reasoning"  # model override
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, headers=headers, data=json.dumps(payload))
print("Status code:", response.status_code)
try:
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print("Error parsing response as JSON:", e)
    print(response.text) 