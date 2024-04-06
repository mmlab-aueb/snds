from ndn.app        import NDNApp
from ndn.encoding   import Name, InterestParam, BinaryStr, FormalName
from typing         import Optional
from mininet.node   import Host
from mininet.log import MininetLogger

import random
import os
import logging
import argparse



# Define a new logging format
standard_logging = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

_logger = MininetLogger(os.path.basename(__file__))
#TODO hardcoded log level
_logger.setLogLevel('debug')
for handler in _logger.handlers:
    handler.setFormatter(logging.Formatter(standard_logging))

# the ndn-app can be found (https://github.com/UCLA-IRL/ndn-python-repo)
app = NDNApp()

rIDs = []

def parse_args(): 

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--r-type",
        type=str, 
        required=True,
        help="Specify the R-type the service will advertise"
    )

    parser.add_argument(
        "--host-name", 
        type=str, 
        required=True,
        help="Specify the host name the service will run in."
    )


    return parser.parse_args()

def advertisement_app_route(r_type: str): 
    return f"/snds/{r_type}"

def advertisement_app_route_registry(r_type: str): 
    return f"/snds/{r_type}_registry"

args = parse_args()

r_type: str = args.r_type
host_name: str = args.host_name

_logger.debug(f"Read R-type from environment: {r_type}\n")
_logger.debug(f"Read host-name from environment: {host_name}\n")

app_route: str = advertisement_app_route(r_type)
app_route_registry: str = advertisement_app_route_registry(r_type)

snds_r_service = Host(host_name)
snds_r_service.cmd(f"nlsrc advertise {app_route}")
snds_r_service.cmd(f"nlsrc advertise {app_route_registry}")



@app.route(app_route)
def on_interest(
    name: FormalName, 
    interest_param: InterestParam, 
    app_param: Optional[BinaryStr]
):
    _logger.info(f"Received Interest: {Name.to_str(name)}\n")

    #create the rID
    r_ID = random.randint(0,200)
    while r_ID in rIDs:
        r_ID = random.randint(0,200)

    rIDs.append(r_ID)

    app.put_data(name, content=(rIDs[-1].to_bytes(2, 'big')), freshness_period=10000)

    _logger.info(f"Data sent: {Name.to_str(name)}\n")

@app.route(app_route_registry)
def on_interest(
    name: FormalName, 
    interest_param: InterestParam, 
    app_param: Optional[BinaryStr]
):
    _logger.info(f"Received Interest: {Name.to_str(name)}\n")

    _logger.debug(f"rIDs: {rIDs}\n")

    app.put_data(name, content=bytes(rIDs), freshness_period=10000)

    _logger.info(f"Data sent: {Name.to_str(name)}\n")




# this file runs inside the producer 
if __name__ == '__main__':

    try:
        _logger.info("Starting SNDS R service\n")
        app.run_forever()
    except Exception as e: 
        # Log the error message
        _logger.error(f"An error occurred: {e}\n")

        # Log the type of the exception
        _logger.error(f"Exception type: {type(e).__name__}\n")

        # Get a full traceback
        import traceback
        tb = traceback.format_exc()
        _logger.error(f"Traceback: {tb}\n")

    except BaseException as e:
        # This will catch everything, including KeyboardInterrupt, SystemExit, etc.
        _logger.error(f"A non-standard exception occurred: {e}\n")
        # Log the type of the exception
        _logger.error(f"Exception type: {type(e).__name__}\n")

        # Get a full traceback
        import traceback
        tb = traceback.format_exc()
        _logger.error(f"Traceback: {tb}\n")

    finally: 
        _logger.info(f"Shutting down R-service for: {host_name}\n")
        app.shutdown()
