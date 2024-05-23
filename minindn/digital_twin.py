import json
import sys
import os

id = sys.argv[1]
TYPE = sys.argv[2]

#Define JSON-LD data as python dictionary 
json_ld_data = {
    "@context": "https://excid-io.github.io/dare/context/ngsi-context.jsonld",
    "@type": TYPE,
    "@id": id,
    "speed": 60,
    "location": {
        "@type": "Address",
        "street": "Trias 2",
        "country": "GR",
        "city": "Athens"
    }    
}

id = id.split(":")[-1]

json_ld_name = "{}.jsonld".format(id)


with open(json_ld_name, "w") as json_ld:
    json.dump(json_ld_data, json_ld, indent=2)


#print(json_ld_data["@type"])

#os.system("export HOME=/tmp/minindn/node2")

os.system('python3 /home/minindn/snds/minindn/SNDS_service.py ' + id + ' ' + json_ld_data["@type"] + ' &')

