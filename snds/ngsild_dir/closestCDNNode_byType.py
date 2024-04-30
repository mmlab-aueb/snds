from ndn.encoding   import Name
from ndn.app        import NDNApp
from ndn.types      import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
from mininet.log    import MininetLogger

import json
import argparse
import os
import logging

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
        '--type', 
        type=str, 
        required=True
    )

    return parser.parse_args()

async def express_interest(interest_name):
    try:
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

    interest_name = '/snds/{}_registry'.format(requested_type)

    _logger.debug(f'Interest name: {interest_name}\n')

    data_name, meta_info, content = await express_interest(interest_name)

    _logger.info(f"Received Data Name in run: {Name.to_str(data_name)}\n")

    rIDs = list(content)

    interest_name = '/snds/{}'.format(rIDs[-1])

    data_name, meta_info, content = await express_interest(interest_name)

    _logger.info(f"Received Data Name: {Name.to_str(data_name)}\n")

    data = bytes(content)
    json_data = json.loads(data.decode())

    _logger.debug(f"JSON DATA RECEIVED: {json_data}\n")

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
