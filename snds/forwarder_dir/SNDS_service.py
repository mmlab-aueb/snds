from ndn.encoding import Name, InterestParam, FormalName, BinaryStr
from ndn.app import NDNApp
from ndn.types import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
from mininet.node import Host
from mininet.log import MininetLogger
from typing import Optional

import random
import json
import logging
import argparse
import os
import shlex

app = NDNApp()

# Define a new logging format
standard_logging = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

_logger = MininetLogger(os.path.basename(__file__))
_logger.setLogLevel('debug')
for handler in _logger.handlers:
    handler.setFormatter(logging.Formatter(standard_logging))

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--host-name", type=str, required=True)
    parser.add_argument("--r-type", type=str, required=True)
    parser.add_argument("--object-name", type=str, required=True)

    return parser.parse_args()

args = parse_args()

# Sanitize inputs
host_name = shlex.quote(args.host_name)
r_type = shlex.quote(args.r_type)
object_name = shlex.quote(args.object_name)

def advertisement_app_route(r_type: str):
    return f"/snds/{r_type}"

def rid_app_route(rid: int):
    return f"/snds/{rid}"

app_route = advertisement_app_route(r_type)

snds_service = Host(host_name)
result = snds_service.cmd(f"nlsrc advertise {app_route}")
_logger.debug(f"Result after running nlsrc advertise {app_route}:\nResult {result}\n")

@app.route(app_route)
def on_interest(name: FormalName, interest_param: InterestParam, app_param: Optional[BinaryStr]):
    _logger.info(f"Received Interest: {Name.to_str(name)}\n")

    with open(f"{object_name}.jsonld", "r") as json_file:
        json_content = json.load(json_file)

    app.put_data(name, content=json.dumps(json_content).encode(), freshness_period=10000)
    _logger.debug(f"Data sent: {Name.to_str(name)}\n")

async def main():
    try:
        nonce = str(random.randint(0,100000000))
        data_name, meta_info, content = await app.express_interest(
            f'/snds/{r_type}/{nonce}',
            must_be_fresh=True,
            can_be_prefix=False,
            lifetime=6000
        )
        _logger.info(f"Received Data Name: {Name.to_str(data_name)}\n")
        _logger.debug(bytes(content) if content else None + "\n")

        rID = str(int.from_bytes(content, 'big'))
        _logger.debug(f"rID received: {rID}\n")

        result = snds_service.cmd(f"nlsrc advertise {rid_app_route(rID)}")

        _logger.debug(f"Result after running nlsrc advertise {rid_app_route(rID)}:\nResult {result}\n")

        @app.route(rid_app_route(rID))
        def on_interest(name: FormalName, interest_param: InterestParam, app_param: Optional[BinaryStr]):
            _logger.info(f"Received Interest: {Name.to_str(name)}\n")

            with open("{}.jsonld".format(object_name), "r") as json_file:
                json_content = json.load(json_file)

            app.put_data(name, content=json.dumps(json_content).encode(), freshness_period=10000)

            _logger.debug(f"Data sent: {Name.to_str(name)}\n")

    except InterestNack as e:
        _logger.error(f'Nacked with reason={e.reason}\n')
        raise e
    except InterestTimeout as e:
        _logger.error('Timeout: {e.reason}\n')
        raise e
    except InterestCanceled as e:
        _logger.error('Canceled: {e.reason}\n')
        raise e
    except ValidationFailure as e:
        _logger.error('Data failed to validate: {e.reason}\n')
        raise e

    except Exception as e:
        _logger.error(f"Non standard exception occured: {e}\n")
        _logger.info(f"Closing SNDS service.\n")
    

if __name__ == '__main__':
    app.run_forever(after_start=main())
