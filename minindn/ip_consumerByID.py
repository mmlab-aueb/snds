import requests
import json
import sys

TYPE = sys.argv[1]
id = sys.argv[2]


#Read a record by id 
print("---Read a single record by id---")

url = "http://localhost:8080"
headers = {
    'Link':'<https://excid-io.github.io/dare/context/ngsi-context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'
}
params = {
    'consumer': 'consumer1',
    'id':'urn:ngsi-ld:Car:' + id
}

response = requests.request("GET", url, headers=headers, params=params)
print(response.text)


