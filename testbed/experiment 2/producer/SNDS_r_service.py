import argparse
import logging
import random

from ndn.app import NDNApp
from ndn.encoding import Name, InterestParam, BinaryStr, FormalName

from typing import Optional

prefix = "/ndn/gr/edu/mmlab2/aueb/fotiou"
snds_type = "Car"

url = "unix:///run/nfd/nfd.sock"

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

app = NDNApp()


rIDs = []


@app.route(prefix + "snds/" + snds_type)
def on_interest(name: FormalName, interest_param: InterestParam, app_param: Optional[BinaryStr]):
    newItemId = Name.to_str(name)
    _logger.info(f"Received Interest: {newItemId}\n")

    rIDs.append(newItemId)
    result="OK"
    app.put_data(name, content=result.encode(), freshness_period=10000)

    _logger.info(f"Data sent: {Name.to_str(name)}\nFrom route: {app_route}\n")

@app.route(prefix + "snds/" + snds_type + "_registry")
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
