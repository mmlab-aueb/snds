import argparse
import logging
import os
import json
import shlex  # Import shlex

from mininet.node import Host
from mininet.log import MininetLogger

# Define a new logging format
standard_logging = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

_logger = MininetLogger(os.path.basename(__file__))
_logger.setLogLevel('debug')
for handler in _logger.handlers:
    handler.setFormatter(logging.Formatter(standard_logging))

def parse_args():
    parser = argparse.ArgumentParser()

    # mininet host name
    parser.add_argument(
        '--host-name',
        type=str,
        required=True,
    )

    parser.add_argument(
        '--id',
        type=str,
        required=True
    )

    parser.add_argument(
        '--r-type',
        type=str,
        required=True,
    )

    return parser.parse_args()


args = parse_args()

r_type = shlex.quote(args.r_type)
id_w = shlex.quote(args.id)
host_name = shlex.quote(args.host_name)

# Define JSON-LD data as python dictionary
json_ld_data = {
    "@context": "https://excid-io.github.io/dare/context/ngsi-context.jsonld",
    "@type": r_type,
    "@id": id_w,
    "speed": 60,
    "location": {
        "@type": "Address",
        "street": "Trias 2",
        "country": "GR",
        "city": "Athens"
    }
}

id_w = id_w.split(":")[-1]  # Sanitize and split the ID to prevent directory traversal and injection
json_ld_name = f"{id_w}.jsonld"  # Use f-string for clarity and security

with open(json_ld_name, "w") as json_ld:
    _logger.debug(f"Writing to JSON file: {json_ld_name}\n")
    json.dump(json_ld_data, json_ld, indent=2)

host = Host(host_name)
result = host.cmd(f'python SNDS_service.py --object-name {id_w} --r-type {json_ld_data["@type"]} --host-name {host_name}')


_logger.debug(f"Result after running SNDS_service with object-name {id_w}, r-type {json_ld_data['@type']} and host-name {host_name}\n:Result {result}\n")

