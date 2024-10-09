import requests

endpoint = "http://localhost:8000/api_app/"

response = requests.get(endpoint,)

print(response.json())