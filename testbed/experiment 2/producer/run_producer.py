import logging
import os
import subprocess
import signal
import sys
import threading
import argparse
import json
import shlex
from didself import registry
from jwcrypto import jwk, jws

# Ensure the logs directory exists
os.makedirs("./logs", exist_ok=True)

# Get the current filename without the extension
log_filename = os.path.splitext(os.path.basename(__file__))[0]

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(f"./logs/{log_filename}.log", mode='w'),  # Overwrite log file each run
                        logging.StreamHandler()
                    ])

# Create a logger
_logger = logging.getLogger(__name__)

# TODO hardcoded log level
_logger.setLevel(logging.DEBUG)


background_processes = []

def signal_handler(sig, frame):
    _logger.info("Ctrl+C pressed. Terminating background processes...")
    for process in background_processes:
        try:
            process.terminate()
            process.wait()  # Wait for the process to terminate
            _logger.info(f"Terminated process with PID: {process.pid}")
        except ProcessLookupError:
            _logger.warning(f"Process with PID {process.pid} already terminated.")
    _logger.info("All background processes terminated. Exiting...")
    sys.exit(0)

# Register the signal handler for SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

def stream_output(process):
    """Function to stream the output of a process to both the console and the log file."""
    for line in iter(process.stdout.readline, ''):
        _logger.info(line.strip())
    process.stdout.close()

json_key = json.dumps({
    "crv":"P-256",
    "d":"3VLckqxXgZeoenHfs6SvrHSiKh_oJc35VR0PKXr7Xws",
    "kty":"EC","x":"FeZdoJ672_EC0TfNT3Dcdt7SVufnK89iHyeZrLomXwA",
    "y":"hSOMgjLBiV2C7VvmifGlqtOBtItVxTpf8j1O-Q2Fg0o"
    })

did_key = jwk.JWK.from_json(json_key)
owner_registry = registry.DIDSelfRegistry(did_key)
authentication_jwk = jwk.JWK.generate(kty='OKP', crv='Ed25519')
# Create JSON-LD data
json_ld_data = {
    "@context": "https://excid-io.github.io/dare/context/ngsi-context.jsonld",
    "@type": "car",
    "@id": "did:self:R1h9F5Oo-eDudLZDe1_1minM0Tjszh2Jpoio7iXRi68",
    "speed": 60,
    "location": {
        "@type": "Address",
        "street": "Trias 2",
        "country": "GR",
        "city": "Athens"
    }
}
x5c = owner_registry.exportX509(authentication_jwk.export_to_pem(password=None),"DER")
jws_header_dict = {
            'alg': "EdDSA",
            'x5c': x5c
        }

jws_header = json.dumps(jws_header_dict)
jws_payload= json.dumps(json_ld_data)
proof = jws.JWS(jws_payload.encode('utf-8'))
proof.add_signature(authentication_jwk, None, jws_header,None)

id_w = "R1h9F5Oo-eDudLZDe1_1minM0Tjszh2Jpoio7iXRi68"  # Sanitize and split the ID to prevent directory traversal and injection
json_ld_name = f"{id_w}.jsonld"  # Use f-string for clarity and security

with open(json_ld_name, "w") as json_ld:
    _logger.debug(f"Writing to JSON file: {json_ld_name}\n")
    json_ld.write(proof.serialize(compact=True))

# Command to run SNDS_r_service.py
command = f"python SNDS_r_service.py --type car"

# Start the command as a background process
process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
background_processes.append(process)

# Start a thread to stream the output
thread = threading.Thread(target=stream_output, args=(process,))
thread.start()

_logger.info(f"Started background process with command: {command}")
_logger.info(f"Background process PID: {process.pid}")

# Log the current list of background process IDs
_logger.info(f"Current background PIDs: {[p.pid for p in background_processes]}")

# Command to run SNDS_service.py
command = f"python SNDS_service.py --object-name {id_w} --type {json_ld_data['@type']}"

# Start the command and capture its output
process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
background_processes.append(process)

# Start a thread to stream the output
thread = threading.Thread(target=stream_output, args=(process,))
thread.start()

_logger.info(f"Started SNDS_service.py background process with command: {command}")
_logger.info(f"Background process PID: {process.pid}")

# Log the current list of background process IDs
_logger.info(f"Current background PIDs: {[p.pid for p in background_processes]}")

_logger.info("Running... Press Ctrl+C to terminate.")
# Wait indefinitely until Ctrl+C is pressed
signal.pause()
