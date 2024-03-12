from http.server    import BaseHTTPRequestHandler, HTTPServer
from urllib.parse   import urlparse, parse_qs
from mininet.node   import Host

import os
import subprocess

#hostName = "localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        #print("Got request!!!")

        query_params = parse_qs(urlparse(self.path).query)

        if "provider" in query_params:

            id = query_params["id"][0]
            TYPE = query_params["type"][0]

            print("Got query from ip provider for id: " + id + " type: " + TYPE)
            os.system('python3 /home/minindn/snds/minindn/digital_twin.py ' + id + ' ' + TYPE)

        elif "consumer" in query_params:
            if "id" in query_params:
                id = query_params["id"][0]

                print("Got query from ip consumer by id: " + id)
                
                result = os.popen('python3 /home/minindn/snds/minindn/closestCDNNode_byID.py ' + id.split(":")[-1]).read()
                
                print(result)

                self.wfile.write(bytes(result, encoding="utf-8"))

            elif "type" in query_params:
                requested_type = query_params["type"][0]
                #print(requested_type)

                print("Got query from ip consumer by type: " + requested_type)

                result = os.popen('python3 /home/minindn/snds/minindn/closestCDNNode_byType.py ' + requested_type).read()

                print(result)

                self.wfile.write(bytes(result, encoding="utf-8"))
        
        return

if __name__ == "__main__":
    webServer = HTTPServer(("0.0.0.0", serverPort), MyServer)
    print("Server started!!!") 
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    
    webServer.server_close()
    print("Server stopped!")