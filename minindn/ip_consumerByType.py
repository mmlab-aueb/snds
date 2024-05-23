import requests
import json
import sys
import time

TYPE = sys.argv[1]
ip = sys.argv[2]

#Read all records of a given type
print("---Read all records of a given type---")

url = "http://" + ip + ":8080"
headers = {
    'Link':'<https://excid-io.github.io/dare/context/ngsi-context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'
}
params = {
    'consumer': 'consumer1',
    'type':TYPE
}

start_time = time.time()
response = requests.request("GET", url, headers=headers, params=params)
end_time = time.time()

print(response.text)
duration = end_time - start_time
print(duration)
