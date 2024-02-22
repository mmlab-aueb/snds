import requests
import json


#Read a record by id 
print("---Read a single record by id---")

url = "http://10.0.0.13:8080"
headers = {
    'Link':'<https://excid-io.github.io/dare/context/ngsi-context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'
}
params = {
    'id':'urn:ngsi-ld:Car:Car1'
}

response = requests.request("GET", url, headers=headers, params=params)
print(response.text)

#Read all records of a given type
print("---Read all records of a given type---")

url = "http://10.0.0.13:8080"
headers = {
    'Link':'<https://excid-io.github.io/dare/context/ngsi-context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'
}
params = {
    'type':'CAR'
}

response = requests.request("GET", url, headers=headers, params=params)

print(response.text)
