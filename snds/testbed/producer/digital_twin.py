import argparse
import logging
import os
import json
import shlex  # Import shlex

# Get the current filename without the extension
log_filename = os.path.splitext(os.path.basename(__file__))[0]

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(f"./logs/{log_filename}.log", mode='w'),
                        logging.StreamHandler()
                    ])

# Create a logger
_logger = logging.getLogger(__name__)

#TODO hardcoded log level
_logger.setLevel('DEBUG')

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--id',
        type=str,
        required=True
    )

    parser.add_argument(
        '--type',
        type=str,
        required=True,
    )

    return parser.parse_args()


args = parse_args()

snds_type = shlex.quote(args.type)
id_w = shlex.quote(args.id)

# Define JSON-LD data as python dictionary
json_ld_data = {
    "@context": "https://excid-io.github.io/dare/context/ngsi-context.jsonld",
    "@type": snds_type,
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

result = os.popen(f"python SNDS_service.py --object-name {id_w} --type {json_ld_data['@type']} &")

_logger.debug(f"Result after running SNDS_service with object-name {id_w}, type {json_ld_data['@type']}")