import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("DATAJUD_API_KEY")
URL = os.getenv("DATAJUD_TJCE_URL")

headers = {
    "Authorization": f"APIKey {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "size": 2,
    "query": {"term": {"orgaoJulgador.codigo": 93861}},
    "sort": [
        {"@timestamp": {"order": "asc"}},
        {"id.keyword": {"order": "asc"}}
    ]
}

response = requests.post(URL, headers=headers, json=payload, timeout=60)
print(f"Tiebreaker id.keyword Status: {response.status_code}")
if response.status_code == 200:
    for h in response.json()["hits"]["hits"]:
        print("Sort with tiebreaker:", h["sort"])
else:
    print(response.text)

