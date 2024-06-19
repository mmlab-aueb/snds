from ndn.encoding import Name, InterestParam, FormalName, BinaryStr
from ndn.app import NDNApp
from ndn.types import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
from typing import Optional

import random
import os
import json
import logging
import argparse
import shlex
import configparser

app = NDNApp()

def read_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config['DEFAULT']['prefix']

prefix = read_config("producer.conf")

# Ensure the logs directory exists
os.makedirs("./logs", exist_ok=True)

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

# TODO hardcoded log level
_logger.setLevel(logging.DEBUG)
# Ensure the logs directory exists
os.makedirs("./logs", exist_ok=True)

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

# TODO hardcoded log level
_logger.setLevel(logging.DEBUG)

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--type", type=str, required=True)
    parser.add_argument("--object-name", type=str, required=True)

    return parser.parse_args()

args = parse_args()

# Sanitize inputs
snds_type = shlex.quote(args.type)
object_name = shlex.quote(args.object_name)

_logger.debug(f"Arguments inside SNDS_service:\nsnds_type: {snds_type}\nobject_name: {object_name}\n")

def advertisement_app_route(object_name: str):
    return f"{prefix}/snds/{object_name}"

def rid_app_route(rid: int):
    return f"{prefix}/snds/{rid}"

app_route = advertisement_app_route(object_name)

@app.route(app_route)
def on_interest(name: FormalName, interest_param: InterestParam, app_param: Optional[BinaryStr]):
    _logger.info(f"Received Interest: {Name.to_str(name)}\nFor route: {app_route}\n")

    with open(f"{object_name}.jsonld", "r") as json_file:
        json_content = json.load(json_file)

    app.put_data(name, content=json.dumps(json_content).encode(), freshness_period=10000)
    _logger.debug(f"Data sent: {Name.to_str(name)}\nFrom route: {app_route}\n")

async def main():
    try:
        nonce = str(random.randint(0,100000000))
        data_name, meta_info, content = await app.express_interest(
            f'{prefix}/snds/{snds_type}/{nonce}',
            must_be_fresh=True,
            can_be_prefix=False,
            lifetime=6000
        )
        _logger.info(f"Received Data Name: {Name.to_str(data_name)}\n")
        _logger.debug(bytes(content) if content else "" + "\n")

        rID = str(int.from_bytes(content, 'big'))
        _logger.debug(f"rID received: {rID}\n")
        
        rid_app_route_str = rid_app_route(rID)

        @app.route(rid_app_route_str)
        def on_interest(name: FormalName, interest_param: InterestParam, app_param: Optional[BinaryStr]):
            _logger.info(f"Received Interest: {Name.to_str(name)}\nFor route: {rid_app_route_str}\n")

            with open("{}.jsonld".format(object_name), "r") as json_file:
                json_content = json.load(json_file)

            app.put_data(name, content=json.dumps(json_content).encode(), freshness_period=10000)

            _logger.debug(f"Data sent: {Name.to_str(name)}\nFrom route: {rid_app_route_str}\n")

    except InterestNack as e:
        _logger.error(f'Nacked with reason={e.reason}\n')
        raise e
    except InterestTimeout as e:
        _logger.error(f'Timeout: {e.reason}\n')
        raise e
    except InterestCanceled as e:
        _logger.error(f'Canceled: {e.reason}\n')
        raise e
    except ValidationFailure as e:
        _logger.error(f'Data failed to validate: {e.reason}\n')
        raise e
    except Exception as e:
        _logger.error(f"Non standard exception occurred: {e}\n")
        _logger.info("Closing SNDS service.\n")
        app.shutdown()
    

if __name__ == '__main__':
    app.run_forever(after_start=main())
