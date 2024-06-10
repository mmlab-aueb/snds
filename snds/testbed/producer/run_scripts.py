import logging
import os
import subprocess

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

background_pids = []

command = "python SNDS_r_service.py --type Car"

# Start the command as a background process
process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Store the process ID
background_pids.append(process.pid)

_logger.info(f"Started background process with command: {command}")
_logger.info(f"Background process PID: {process.pid}")

# Log the current list of background process IDs
_logger.info(f"Current background PIDs: {background_pids}")

command = "python digital_twin.py --id 1 --type Car"

result = os.popen(cmd=command).read()

_logger.info(f"Result after running: {command} is: {result}")
# Optional: If you want to check the output or errors in a non-blocking manner
#stdout, stderr = process.communicate()
#_logger.debug(f"Process stdout: {stdout.decode('utf-8')}")
#_logger.debug(f"Process stderr: {stderr.decode('utf-8')}")



