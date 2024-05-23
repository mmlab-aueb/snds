import requests
import json
import sys

TYPE = sys.argv[1]
id = sys.argv[2]
ip = sys.argv[3]


url = "http://" + ip + ":8080"
headers = {
    'Link':'<https://excid-io.github.io/dare/context/ngsi-context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'
}
params = {
    'provider': 'provider1',
    'id': 'urn:ngsi-ld:' + TYPE + ':' + id,
    'type': TYPE
}

response = requests.request("GET", url, headers=headers, params=params)
print(response.text)

