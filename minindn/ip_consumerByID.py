import requests
import json
import sys
import time

TYPE = sys.argv[1]
id = sys.argv[2]
ip = sys.argv[3]


#Read a record by id 
print("---Read a single record by id---")

url = "http://" + ip + ":8080"
headers = {
    'Link':'<https://excid-io.github.io/dare/context/ngsi-context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'
}
params = {
    'consumer': 'consumer1',
    'id': 'urn:ngsi-ld:' + TYPE + ':' + id
}

start_time = time.time()
response = requests.request("GET", url, headers=headers, params=params)
end_time = time.time()
print(response.text)
duration = end_time - start_time
print(duration)