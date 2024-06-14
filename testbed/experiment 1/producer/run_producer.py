import logging
import os
import subprocess
import signal
import sys
import threading
import argparse
import json
import shlex

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--type",
        type=str,
        required=True,
    )

    parser.add_argument(
        "--id",
        type=str,
        required=True,
    )

    return parser.parse_args()

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

args = parse_args()
snds_type = shlex.quote(args.type)
snds_id = shlex.quote(args.id)

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

# Create JSON-LD data
json_ld_data = {
    "@context": "https://excid-io.github.io/dare/context/ngsi-context.jsonld",
    "@type": snds_type,
    "@id": snds_id,
    "speed": 60,
    "location": {
        "@type": "Address",
        "street": "Trias 2",
        "country": "GR",
        "city": "Athens"
    }
}

id_w = snds_id.split(":")[-1]  # Sanitize and split the ID to prevent directory traversal and injection
json_ld_name = f"{id_w}.jsonld"  # Use f-string for clarity and security

with open(json_ld_name, "w") as json_ld:
    _logger.debug(f"Writing to JSON file: {json_ld_name}\n")
    json.dump(json_ld_data, json_ld, indent=2)

# Command to run SNDS_r_service.py
command = f"python SNDS_r_service.py --type {snds_type}"

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
