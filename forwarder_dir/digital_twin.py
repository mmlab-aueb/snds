import json

#Define JSON-LD data as python dictionary 
json_ld_data = {
    "@context": "https://excid-io.github.io/dare/context/ngsi-context.jsonld",
    "@type": "CAR",
    "@id": "urn:ngsi-ld:Car:Car1",
    "speed": 60,
    "location": {
        "@type": "Address",
        "street": "Trias 2",
        "country": "GR",
        "city": "Athens"
    }    
}

json_ld_name = "car1.jsonld"

with open(json_ld_name, "w") as json_ld_car1:
    json.dump(json_ld_data, json_ld_car1, indent=2)