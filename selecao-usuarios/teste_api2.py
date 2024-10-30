import requests
import json
url = "https://mesageria-mvp-567502497958.us-central1.run.app/passo2"
payload = {}
headers = {
  'X-API-Key': 'P^g8@Xf@JrA&0pAbrT',
  'Content-Type': 'application/json'
}
response = requests.request("GET", url, headers=headers, data=payload)
print(response.text)