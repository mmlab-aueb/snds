from ndn.encoding import Name, InterestParam, FormalName, BinaryStr
from ndn.app import NDNApp
from ndn.types import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
from jwcrypto import jwk, jws

from typing import Optional
import random
import os
import json
import logging
import time


app = NDNApp()
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



@app.route(prefix + "/snds/iQ9PsBKOH1nLT9FyhsUGvXyKoW00yqm_-_rVa3W7Cl0")
def on_interest(name: FormalName, interest_param: InterestParam, app_param: Optional[BinaryStr]):
    _logger.info(f"Received Interest: {Name.to_str(name)}\nFor route: {app_route}\n")

    with open(f"Data/iQ9PsBKOH1nLT9FyhsUGvXyKoW00yqm_-_rVa3W7Cl0/{object_name}.jsonld", "r") as json_file:
        json_content = json.load(json_file)

    app.put_data(name, content=json.dumps(json_content).encode(), freshness_period=10000)
    _logger.debug(f"Data sent: {Name.to_str(name)}\nFrom route: {app_route}\n")

async def main():
    try:
        signing_key = jwk.JWK.generate(kty='EC', crv='P-256')
        jws_header_dict = {
            'alg': 'ES256',
        }
        jws_payload_dict = {
            "exp": int(time.time()) + 600,
            "iat": int(time.time()),
            "nonce":"this is a nonce"
        }
        jws_payload = json.dumps(jws_payload_dict)
        jws_header = json.dumps(jws_header_dict)
        proof = jws.JWS(jws_payload.encode('utf-8'))
        proof.add_signature(signing_key, None, jws_header,None)

        data_name, meta_info, content = await app.express_interest(
            f'{prefix}/snds/Car/iQ9PsBKOH1nLT9FyhsUGvXyKoW00yqm_-_rVa3W7Cl0/car2',
            proof.serialize().encode(),
            must_be_fresh=True,
            can_be_prefix=False,
            lifetime=6000
        )
        _logger.info(f"Received Data Name: {Name.to_str(data_name)}\n")
        print("Registration result:")
        data = bytes(content)
        print(data)
        _logger.debug(bytes(content) if content else "" + "\n")

        

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
