import os
import logging

from http.server    import BaseHTTPRequestHandler, HTTPServer
from urllib.parse   import urlparse, parse_qs
from mininet.node   import Host
from mininet.log    import MininetLogger
#from dotenv import load_dotenv

#load_dotenv()

#TODO hardcoded port and ip
hostName = "0.0.0.0"
serverPort = 8080

#hostName = os.getenv('HTTP_PROXY_HOSTNAME')
#serverPort = os.getenv('HTTP_PROXY_PORT')


class MyServer(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        self._set_headers()

        host = Host('closest')
        host.cmd('export HOME=/tmp/minindn/closest')

        query_params = parse_qs(urlparse(self.path).query)
        if "id" in query_params:
            id = query_params["id"][0]
            _logger.debug(f"Received ID in do_GET: {id}\n")

            result = host.cmd('python closestCDNNode_byID.py ' + id.split(":")[-1])

            _logger.debug(f"Result after running: python closestCDNNode_byID.py\nResult: {result}\n")

            self.wfile.write(bytes(result, encoding="utf-8"))
        elif "type" in query_params:
            requested_type = query_params["type"][0]
            _logger.debug(f"Received requested_type: {requested_type} in do_GET.\n")
            
            result = host.cmd('python closestCDNNode_byType.py ' + requested_type)

            _logger.debug(f"Result after running: python3 closestCDNNode_byType.py\nResult: {result}\n")

            self.wfile.write(bytes(result, encoding="utf-8"))
        
        return

if __name__ == "__main__":

    # Define a new logging format
    standard_logging = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    _logger = MininetLogger(os.path.basename(__file__))
    #TODO hardcoded log level
    _logger.setLogLevel('debug')
    for handler in _logger.handlers:
        handler.setFormatter(logging.Formatter(standard_logging))

    webServer = HTTPServer((hostName, serverPort), MyServer)
    _logger.info(f"Server started at http://{hostName}:{serverPort}\n")
    try:
        webServer.serve_forever()
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
        _logger.info("Server stopped!\n")
        webServer.server_close()
