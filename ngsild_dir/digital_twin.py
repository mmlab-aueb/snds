import argparse
import logging
import os
import json

from mininet.node   import Host
from mininet.log    import MininetLogger

# Define a new logging format
standard_logging = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

_logger = MininetLogger(os.path.basename(__file__))
#TODO hardcoded log level
_logger.setLogLevel('debug')
for handler in _logger.handlers:
    handler.setFormatter(logging.Formatter(standard_logging))

def parse_args(): 

    parser = argparse.ArgumentParser()

    # mininet host name
    parser.add_arguments(
        '--host-name',
        type=str, 
        required=True,
    )

    parser.add_arguments(
        '--id', 
        type=str, 
        required=True
    )

    parser.add_arguments(
        '--r-type',
        type=str,
        required=True,
    )

    return parser.parse_args()


args = parse_args()

r_type = args.r_type
id = args.id
host_name = args.host_name

#Define JSON-LD data as python dictionary 
json_ld_data = {
    "@context": "https://excid-io.github.io/dare/context/ngsi-context.jsonld",
    "@type": r_type,
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

host = Host(host_name)
host.cmd(f'python /mini-ndn/app/SNDS_service.py --object-name {id} --r-type {json_ld_data["@type"]} --host-name {host_name}')

