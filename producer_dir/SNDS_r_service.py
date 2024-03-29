from ndn.app        import NDNApp
from ndn.encoding   import Name, InterestParam, BinaryStr, FormalName
from typing         import Optional
from mininet.node   import Host
from mininet.log import MininetLogger

import random
import base64
import os
import logging

app = NDNApp()

class SndsRService: 

    def __init__(self): 
        #TODO hardcoded endpoints
        snds_r_service = Host('producer')
        snds_r_service.cmd('nlsrc advertise /snds/CAR')
        snds_r_service.cmd('nlsrc advertise /snds/CAR_registry')

        self.rID=[]


    @app.route('/snds/CAR')
    def on_interest(name: FormalName, interest_param: InterestParam, app_param: Optional[BinaryStr]):
        _logger.info(f"Received Interest: {Name.to_str(name)}\n")

        #create the rID
        r_ID = random.randint(0,200)
        while r_ID in self.rID:
            r_ID = random.randint(0,200)

        self.rID.append(r_ID)

        app.put_data(name, content=(self.rID[-1].to_bytes(2, 'big')), freshness_period=10000)

        _logger.info(f"Data sent: {Name.to_str(name)}\n")

    @app.route('/snds/CAR_registry')
    def on_interest(name: FormalName, interest_param: InterestParam, app_param: Optional[BinaryStr]):
        _logger.info(f"Received Interest: {Name.to_str(name)}\n")

        _logger.debug(f"rID: {self.rID}\n")

        app.put_data(name, content=bytes(self.rID), freshness_period=10000)

        _logger.info(f"Data sent: {Name.to_str(name)}\n")

if __name__ == '__main__':
    # Define a new logging format
    standard_logging = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    _logger = MininetLogger(os.path.basename(__file__))
    #TODO hardcoded log level
    _logger.setLogLevel('debug')
    for handler in _logger.handlers:
        handler.setFormatter(logging.Formatter(standard_logging))

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
        _logger.info("Shutting down producer\n")
        app.shutdown()
