import requests

url = "http://localhost:8000/rules/enforce/validate_data_types"
payload = {
    "data": [
        {"id": 1, "value": "test"},
        {"id": "2", "value": "test2"}
    ]
}
response = requests.post(url, json=payload)
print(response.status_code)
print(response.json()) 