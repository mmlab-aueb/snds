import requests
import json
import sys

TYPE = sys.argv[1]

#Read all records of a given type
print("---Read all records of a given type---")

url = "http://localhost:8080"
headers = {
    'Link':'<https://excid-io.github.io/dare/context/ngsi-context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'
}
params = {
    'consumer': 'consumer1',
    'type':TYPE
}

response = requests.request("GET", url, headers=headers, params=params)

print(response.text)
