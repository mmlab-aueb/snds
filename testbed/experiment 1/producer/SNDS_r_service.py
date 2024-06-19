import argparse
import logging
import shlex
import random
import configparser

from ndn.app import NDNApp
from ndn.encoding import Name, InterestParam, BinaryStr, FormalName

from typing import Optional

# Configure the logger
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(f"./logs/{__name__}.log"),
                        logging.StreamHandler()
                    ])

# Create a logger
_logger = logging.getLogger(__name__)

# Define a new logging format
standard_logging = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

def read_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config['DEFAULT']['prefix']

prefix = read_config("producer.conf")

_logger.debug(f"Read prefix from config: {prefix}")

url = "unix:///run/nfd/nfd.sock"


app = NDNApp()


rIDs = []

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--type",
        type=str,
        required=True,
    )

    return parser.parse_args()

def advertisement_app_route(snds_type: str):
    return f"/snds/{snds_type}"

def advertisement_app_route_registry(snds_type: str):
    return f"/snds/{snds_type}_registry"

args = parse_args()

# Sanitize inputs
snds_type: str = shlex.quote(args.type)

app_route: str = advertisement_app_route(snds_type)
app_route_registry: str = advertisement_app_route_registry(snds_type)

_logger.debug(f"Read SNDS-type from environment: {snds_type}\n")

_logger.debug(f"App route: {app_route}\n")
_logger.debug(f"App route registry: {app_route_registry}\n")


@app.route(prefix + app_route)
def on_interest(name: FormalName, interest_param: InterestParam, app_param: Optional[BinaryStr]):
    _logger.info(f"Received Interest: {Name.to_str(name)}\nFor route: {app_route}\n")

    # Create the rID
    r_ID = random.randint(0,200)
    while r_ID in rIDs:
        r_ID = random.randint(0,200)

    rIDs.append(r_ID)

    app.put_data(name, content=(rIDs[-1].to_bytes(2, 'big')), freshness_period=10000)

    _logger.info(f"Data sent: {Name.to_str(name)}\nFrom route: {app_route}\n")

@app.route(prefix + app_route_registry)
def on_interest(name: FormalName, interest_param: InterestParam, app_param: Optional[BinaryStr]):
    _logger.info(f"Received Interest: {Name.to_str(name)}\nFor route: {app_route_registry}\n")

    _logger.debug(f"rIDs: {rIDs}\n")

    app.put_data(name, content=bytes(rIDs), freshness_period=10000)

    _logger.info(f"Data sent: {Name.to_str(name)}\nFrom route: {app_route_registry}\n")

# This file runs inside the producer
if __name__ == '__main__':
    try:
        _logger.info("Starting SNDS R service\n")
        app.run_forever()
    except Exception as e:
        _logger.error(f"An error occurred: {e}\n")
        _logger.error(f"Exception type: {type(e).__name__}\n")
        import traceback
        tb = traceback.format_exc()
        _logger.error(f"Traceback: {tb}\n")
    except BaseException as e:
        _logger.error(f"A non-standard exception occurred: {e}\n")
        _logger.error(f"Exception type: {type(e).__name__}\n")
        import traceback
        tb = traceback.format_exc()
        _logger.error(f"Traceback: {tb}\n")
    finally:
        _logger.info("Shutting down R-service\n")
        app.shutdown()
