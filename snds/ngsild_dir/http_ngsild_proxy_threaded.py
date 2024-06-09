import os
import logging
import argparse
import shlex
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs
from mininet.log import MininetLogger
from concurrent.futures import ThreadPoolExecutor

# Define a new logging format
standard_logging = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

_logger = MininetLogger(os.path.basename(__file__))
_logger.setLogLevel('debug')
for handler in _logger.handlers:
    handler.setFormatter(logging.Formatter(standard_logging))

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host-name', type=str, required=True)
    parser.add_argument("--host-ip", type=str, required=True, help="Specify the IP for the webserver.")
    parser.add_argument("--server-port", type=str, required=True, help="Specify the port the webserver listens to.")
    return parser.parse_args()

class ThreadPooledHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    def __init__(self, server_address, HandlerClass, bind_and_activate=True):
        super().__init__(server_address, HandlerClass, bind_and_activate)
        self.executor = ThreadPoolExecutor(max_workers=10)  # Define the size of the thread pool

    def process_request(self, request, client_address):
        """Override the process_request to utilize ThreadPoolExecutor."""
        self.executor.submit(self.process_request_thread, request, client_address)

class MyServer(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        self._set_headers()

        query_params = parse_qs(urlparse(self.path).query)

        if "provider" in query_params:
            id = shlex.quote(query_params["id"][0])
            snds_type = shlex.quote(query_params["type"][0])
            _logger.debug(f"Got query IP provider for id: {id} and type: {snds_type}\n")
            command = f"python digital_twin.py --host-name {host_name} --id {id} --type {snds_type}"
            result = os.popen(command).read()
            _logger.debug(f"Result after running: {command}\nResult: {result}\n")
            self.wfile.write(bytes(result, "utf-8"))
            self.wfile.flush()
            return

        if "id" in query_params:
            id = shlex.quote(query_params["id"][0])
            _logger.debug(f"Received ID in do_GET: {id}\n")
            command = f'python closestCDNNode_byID.py --id {id.split(":")[-1]}'
            result = os.popen(command).read()
            _logger.debug(f"Result after running: {command}\nResult: {result}\n")
            self.wfile.write(bytes(result, "utf-8"))
            self.wfile.flush()
            return

        if "type" in query_params:
            requested_type = shlex.quote(query_params["type"][0])
            _logger.debug(f"Received requested_type: {requested_type} in do_GET.\n")
            command = f'python closestCDNNode_byType.py --type {requested_type}'
            result = os.popen(command).read()
            _logger.debug(f"Result after running: {command}\nResult: {result}\n")
            self.wfile.write(bytes(result, "utf-8"))
            self.wfile.flush()
            return

if __name__ == "__main__":
    args = parse_args()
    host_ip = args.host_ip
    server_port = int(args.server_port)
    host_name = args.host_name

    _logger.debug(f"Read host_ip from environment: {host_ip}\n")
    _logger.debug(f"Read server_port from environment: {server_port}\n")
    _logger.debug(f"Read host_name from environment: {host_name}\n")

    webServer = ThreadPooledHTTPServer((host_ip, server_port), MyServer)
    _logger.info(f"Server started at http://{host_ip}:{server_port}\n")
    try:
        webServer.serve_forever()
    except Exception as e:
        _logger.error(f"An error occurred: {e}\n")
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
        webServer.shutdown()
        webServer.server_close()
        _logger.info("Server stopped!\n")
