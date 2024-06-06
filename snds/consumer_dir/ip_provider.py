import asyncio
import os
import logging
import argparse
import time

from mininet.log    import MininetLogger

from snds.http_utils import get_request

# Define a new logging format
standard_logging = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

_logger = MininetLogger(os.path.basename(__file__))
#TODO hardcoded log level
_logger.setLogLevel('debug')

for handler in _logger.handlers:
    handler.setFormatter(logging.Formatter(standard_logging))

def parse_args(): 

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--type",
        type=str, 
        required=True,
    )

    parser.add_argument(
        "--id", 
        type=str, 
        required=True,
    )

    parser.add_argument(
        "--ip", 
        type=str,
        required=True,
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        required=True,
    )

    return parser.parse_args()

args = parse_args()

ip = args.ip
snds_type = args.type
id = args.id
port = args.port


_logger.info("---Something is happening here with the provider---\n")

url = f"http://{ip}:{port}"

headers = {
    'Link':'<https://excid-io.github.io/dare/context/ngsi-context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'
}

params = {
    'provider': 'provider1',
    'id': f'urn:ngsi-ld:{snds_type}:{id}',
    'type': snds_type,
}

start_time = time.time()
response = asyncio.run(get_request(url=url, headers=headers, params=params))
end_time = time.time()

_logger.info(f"Response received by {url}\n{response}\n")
_logger.info(f"Time the request took: {end_time - start_time}\n")
