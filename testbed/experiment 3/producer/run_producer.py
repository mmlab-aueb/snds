import logging
import os
import subprocess
import signal
import sys
import threading
import argparse
import json
import base64
from ursa_bbs_signatures import ProofMessage, ProofMessageType, CreateProofRequest, create_proof
from ursa_bbs_signatures import BlsKeyPair, sign, SignRequest, VerifyProofRequest, verify_proof


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

def _get_disclosures(json_object, disclosures, prefix):
    if isinstance(json_object, dict):
        for key, value in json_object.items():
            claim =  prefix + "/" + key
            disclosures.append([claim,value])
            if isinstance(value, dict) or isinstance(value, list):
                _get_disclosures(value, disclosures, claim)
    elif isinstance(json_object, list):
        for key in range(len(json_object)):
            claim =  prefix + "/" + str(key)
            value = json_object[key]
            disclosures.append([claim,value])
            if isinstance(value, dict) or isinstance(value, list):
                _get_disclosures(value, disclosures, claim)
    return disclosures
    

def disclosures(json_object):
    claims = _get_disclosures(json_object, [], "")
    return claims

def _set_claim(json_object, keys, value):
    key = keys[0]
    if key not in json_object:
        json_object[key]={}
    if (len(keys)==1):
        json_object[key]=value
    else:
        keys.pop(0)
        _set_claim(json_object[key], keys, value) 

def json_object(disclosures):
    output = {}
    for disclosure in disclosures:
        claim = disclosure[0]
        value = disclosure[1]
        keys = claim.split("/")
        keys.pop(0) # remove $
        _set_claim(output,keys,value)
    return output

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

json_object =  json_ld_data
all_disclosures = disclosures(json_object)
all_disclosures_b64 = base64.b64encode(json.dumps(all_disclosures).encode()).decode()
proof_object = []
public_bls_key = b"\x86M\xc0cUPQ\xdb\xdblE\x87E\x832p8\xf5\xb9\xbeM\x05\xf1G\x9emHe\x99\xf0T\xbfn\x85" \
                              b"\x18\xdb\x86'W\x1c\xe3" \
                              b"\x8aG\x97S\x01\xda\xfe\x0e\x15)\x144I\xf9\xd0:\xcc\xdb\xc5\xc26\x10\xf9@\xaa\x18\xf5," \
                              b"6Es\xfd\xc7\xf1tcZ\x98\xfe\xd6\xcct\xbfk\xfb\x9f\xf1\xad)\x15\x88w\x80\xdd\xea "
secret_bls_key = b'\x06\xe7w\xf4\x90\x0e\xacK\xb7\x94l\x00/\xaaFD\x1c\xff\x9c\xad\xdcq\xed\xb6#%\x7fu' \
                              b'\xc7\x8c\xfe\x9c '

for item in all_disclosures:
    proof_object.append(json.dumps(item))
key_pair = BlsKeyPair(public_bls_key, secret_bls_key)
sign_request = SignRequest(key_pair, proof_object)
signature = sign(sign_request)

id_w = "R1h9F5Oo-eDudLZDe1_1minM0Tjszh2Jpoio7iXRi68"  # Sanitize and split the ID to prevent directory traversal and injection
json_ld_name = f"{id_w}.jsonld"  # Use f-string for clarity and security

with open(json_ld_name, "w") as json_ld:
    _logger.debug(f"Writing to JSON file: {json_ld_name}\n")
    json_ld.write( base64.b64encode(signature).decode())
    json_ld.write(".")
    json_ld.write(base64.b64encode(json.dumps(json_ld_data)).decode())

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
