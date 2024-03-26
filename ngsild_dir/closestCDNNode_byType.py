from ndn.encoding   import Name, InterestParam, FormalName, BinaryStr
from ndn.app        import NDNApp
from ndn.types      import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
from mininet.node   import Host
from typing         import Optional

import sys 
import json

app = NDNApp()

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
        _logger.error(f'Timeout')
    except InterestCanceled:
        _logger.error(f'Canceled')
    except ValidationFailure:
        _logger.error(f'Data failed to validate')

async def run():
    # run inside the http_ngsild_proxy using 
    # python closestCDNNode_byType requested_type
    requested_type = sys.argv[1]

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

    app.shutdown()

if __name__ == '__main__':
    # Define a new logging format
    standard_logging = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    _logger = MininetLogger(os.path.basename(__file__))
    #TODO hardcoded log level
    _logger.setLogLevel('debug')
    for handler in _logger.handlers:
        handler.setFormatter(logging.Formatter(standard_logging))

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
