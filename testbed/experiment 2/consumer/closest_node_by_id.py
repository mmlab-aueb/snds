from ndn.encoding   import Name
from ndn.app        import NDNApp
from ndn.types      import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure

import json
import argparse
import logging
import os
import configparser

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

def read_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config['DEFAULT']['prefix']

prefix = read_config("consumer.conf")

_logger.debug(f"Read prefix from config: {prefix}")


async def run():
    try:
        id="R1h9F5Oo-eDudLZDe1_1minM0Tjszh2Jpoio7iXRi68"
        _logger.info(f"Expressing interest on id: {id}\n")
        data_name, meta_info, content = await app.express_interest (
            f'{prefix}/snds/{id}',
            must_be_fresh=True,
            can_be_prefix=False,
            lifetime=6000
        )

        _logger.info(f"Received data_name in run: {Name.to_str(data_name)}\n")
        _logger.info(f"Received meta_info in run: {meta_info}\n")
        _logger.info(f"Received content in run: {content}\n")
        
        data = bytes(content)
        json_data = json.loads(data.decode())

        _logger.debug(f"RECEIVED JSON DATA: {json_data}\n")

        json_ld_name = "{}.jsonld".format(id)

        with open(json_ld_name, "w") as json_ld:
            json.dump(json_data, json_ld, indent=2)


    except InterestNack as e:
        _logger.error(f'Nacked with reason={e.reason}\n')
        raise e
    except InterestTimeout as e:
        _logger.error('Timeout\n')
        raise e
    except InterestCanceled as e:
        _logger.error('Canceled\n')
        raise e
    except ValidationFailure as e:
        _logger.error('Data failed to validate\n')
        raise e
    finally:
        app.shutdown()

if __name__ == '__main__':
    
 

    id: str = "R1h9F5Oo-eDudLZDe1_1minM0Tjszh2Jpoio7iXRi68"

    _logger.debug(f"Read ID from environment variable: {id}\n")

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