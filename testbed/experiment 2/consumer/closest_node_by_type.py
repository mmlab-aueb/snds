from ndn.encoding   import Name
from ndn.app        import NDNApp
from ndn.types      import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure

import json
import argparse
import logging
import os

prefix = "/ndn/gr/edu/mmlab2/aueb/fotiou"
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

    parser.add_argument(
        '--type', 
        type=str, 
        required=True
    )

    return parser.parse_args()

async def express_interest(interest_name):
    try:
        _logger.info(f"Expressing interest on: {interest_name}\n")
        data_name, meta_info, content = await app.express_interest (
            interest_name,
            must_be_fresh=True,
            can_be_prefix=False,
            lifetime=6000
        )
        return data_name, meta_info, content
    except InterestNack as e:
        _logger.error(f'Nacked with reason={e.reason}')
    except InterestTimeout:
        _logger.error('Timeout')
    except InterestCanceled:
        _logger.error('Canceled')
    except ValidationFailure:
        _logger.error('Data failed to validate')

async def run():

    args = parse_args()

    requested_type: str = args.type

    interest_name = '{}/snds/{}_registry'.format(prefix, requested_type)

    _logger.debug(f'Interest name: {interest_name}\n')

    data_name, meta_info, content = await express_interest(interest_name)

    _logger.info(f"Received data_name in run: {Name.to_str(data_name)}\n")
    _logger.info(f"Received meta_info in run: {meta_info}\n")
    _logger.info(f"Received content in run: {list(content)}\n")

    rIDs = list(content)

    interest_name = '{}/snds/{}'.format(prefix, rIDs[-1])

    data_name, meta_info, content = await express_interest(interest_name)

    _logger.info(f"Received data_name in run: {Name.to_str(data_name)}\n")
    _logger.info(f"Received meta_info in run: {meta_info}\n")
    _logger.info(f"Received content in run: {bytes(content).decode()}\n")

    data = bytes(content)
    json_data = json.loads(data.decode())

    _logger.debug(f"JSON DATA RECEIVED: {json_data}\n")

    json_ld_name = "{}.jsonld".format(json_data["@id"].split(":")[-1])

    with open(json_ld_name, "w") as json_ld:
        json.dump(json_data, json_ld, indent=2)

    app.shutdown()

if __name__ == '__main__':

    app = NDNApp()
    try: 
        app.run_forever(after_start=run())
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