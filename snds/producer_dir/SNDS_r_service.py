import argparse
import logging
import os
import shlex
import random
import subprocess 

from ndn.app import NDNApp
from ndn.encoding import Name, InterestParam, BinaryStr, FormalName
from mininet.log import MininetLogger

from typing import Optional

# Define a new logging format
standard_logging = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

_logger = MininetLogger(os.path.basename(__file__))
_logger.setLogLevel('debug')
for handler in _logger.handlers:
    handler.setFormatter(logging.Formatter(standard_logging))

# the ndn-app can be found at https://github.com/UCLA-IRL/ndn-python-repo
app = NDNApp()

rIDs = []

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--type",
        type=str,
        required=True,
    )

    parser.add_argument(
        "--host-name",
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
host_name: str = shlex.quote(args.host_name)

app_route: str = advertisement_app_route(snds_type)
app_route_registry: str = advertisement_app_route_registry(snds_type)

_logger.debug(f"Read SNDS-type from environment: {snds_type}\n")
_logger.debug(f"Read host-name from environment: {host_name}\n")

_logger.debug(f"App route: {app_route}\n")
_logger.debug(f"App route registry: {app_route_registry}\n")

#snds_r_service = Host(host_name)

# Function to run a command and return a combined result
def run_subprocess(command):
    result = subprocess.run(command, capture_output=True, text=True)
    # Combining stdout, stderr, and return code into a single string
    combined_output = f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}\nReturn Code: {result.returncode}\n"
    return combined_output


result = run_subprocess(["nlsrc", "advertise", app_route])
_logger.debug(f"Result after running nlsrc advertise {app_route}:\nResult: {result}\n")


result = run_subprocess(["nlsrc", "advertise", app_route_registry])
_logger.debug(f"Result after running nlsrc advertise {app_route_registry}:\nResult: {result}\n")

#subprocess.run(["nlsrc", "advertise", app_route_registry])

#result = snds_r_service.cmd(f"nlsrc advertise {app_route}")
#_logger.debug(f"Result after running nlsrc advertise {app_route}:\nResult: {result}\n")
#result = snds_r_service.cmd(f"nlsrc advertise {app_route_registry}")
#_logger.debug(f"Result after running nlsrc advertise {app_route_registry}:\nResult: {result}\n")

@app.route(app_route)
def on_interest(name: FormalName, interest_param: InterestParam, app_param: Optional[BinaryStr]):
    _logger.info(f"Received Interest: {Name.to_str(name)}\nFor route: {app_route}\n")

    # Create the rID
    r_ID = random.randint(0,200)
    while r_ID in rIDs:
        r_ID = random.randint(0,200)

    rIDs.append(r_ID)

    app.put_data(name, content=(rIDs[-1].to_bytes(2, 'big')), freshness_period=10000)

    _logger.info(f"Data sent: {Name.to_str(name)}\nFrom route: {app_route}\n")

@app.route(app_route_registry)
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
        _logger.info(f"Shutting down R-service for: {host_name}\n")
        app.shutdown()