import os
import logging
import argparse
import shlex

from http.server    import BaseHTTPRequestHandler, HTTPServer
from urllib.parse   import urlparse, parse_qs
from mininet.node   import Host
from mininet.log    import MininetLogger

# Define a new logging format
standard_logging = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

_logger = MininetLogger(os.path.basename(__file__))
#TODO hardcoded log level
_logger.setLogLevel('debug')
for handler in _logger.handlers:
    handler.setFormatter(logging.Formatter(standard_logging))

def parse_args():
    
    parser = argparse.ArgumentParser()

    # THE MININDN host name
    parser.add_argument(
        '--host-name',
        type=str, 
        required=True,
    )

    parser.add_argument(
        "--host-ip",
        type=str,
        required=True, 
        help="Specify the IP for the webserver."
    )

    parser.add_argument(
        "--server-port",
        type=str,
        required=True,
        help="Specify the port the webserver listens to."
    )

    args = parser.parse_args()

    return args

class MyServer(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        self._set_headers()

        host = Host(host_name)
        query_params = parse_qs(urlparse(self.path).query)

        if "provider" in query_params:
            id = shlex.quote(query_params["id"][0])
            r_type = shlex.quote(query_params["type"][0])

            _logger.debug(f"Got query IP provider for id: {id} and type: {r_type}\n")
            host.cmd(f"python digital_twin.py --id {id} --r-type {r_type}")
            return

        if "id" in query_params:
            id = shlex.quote(query_params["id"][0])
            _logger.debug(f"Received ID in do_GET: {id}\n")
            result = host.cmd(f'python closestCDNNode_byID.py --id {id.split(":")[-1]}')
            _logger.debug(f"Result after running: python closestCDNNode_byID.py\nResult: {result}\n")
            self.wfile.write(bytes(result, "utf-8"))
            return

        if "type" in query_params:
            requested_type = shlex.quote(query_params["type"][0])
            _logger.debug(f"Received requested_type: {requested_type} in do_GET.\n")
            result = host.cmd(f'python closestCDNNode_byType.py --type {requested_type}')
            _logger.debug(f"Result after running: python closestCDNNode_byType.py\nResult: {result}\n")
            self.wfile.write(bytes(result, "utf-8"))
            return

if __name__ == "__main__":

    args = parse_args()

    host_ip: str = args.host_ip
    server_port: str = args.server_port
    host_name: str = args.host_name

    _logger.debug(f"Read host_ip from environment: {host_ip}\n")
    _logger.debug(f"Read server_port from environment: {server_port}\n")
    _logger.debug(f"Read host_name from environment: {host_name}\n")

    
    webServer = HTTPServer((host_ip, int(server_port)), MyServer)
    _logger.info(f"Server started at http://{host_ip}:{server_port}\n")
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
