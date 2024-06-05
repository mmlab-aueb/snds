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
        required=True,
    )

    return parser.parse_args()
#Read a record by id 
_logger.info("---Read a single record by id---\n")

args = parse_args()

ip = args.ip
id = args.id 
port = args.port

url = f"http://{ip}:{port}"

headers = {
    'Link':'<https://excid-io.github.io/dare/context/ngsi-context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"',
}

params = {
    #TODO what in the name of god is this?
    'consumer': 'consumer1',
    'id':f'urn:ngsi-ld:Car:{id}',
}

start_time = time.time()
response = asyncio.run(get_request(url=url, headers=headers, params=params))
end_time = time.time()

_logger.info(f"Received response from {url}\n{response}\n")
_logger.info(f"Time the request took: {end_time - start_time}\n")
