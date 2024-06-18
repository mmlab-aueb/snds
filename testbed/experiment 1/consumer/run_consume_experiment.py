import os
import argparse
import logging
import cProfile
import pstats
import io

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

args = parse_args()
snds_type = args.type
snds_id = args.id

def run_command_with_profiling(command):
    pr = cProfile.Profile()
    pr.enable()

    result = os.popen(command).read()

    pr.disable()
    
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats(pstats.SortKey.CUMULATIVE)
    ps.print_stats()
    
    _logger.info(f"Command: {command}\nResult: {result}\nProfile Stats:\n{s.getvalue()}")
    return result, s.getvalue()

command = f"python closest_node_by_id.py --id {snds_id}"
result, profile_stats = run_command_with_profiling(command)
_logger.info(f"Profiling Info: Command: {command}\nProfile Stats:\n{profile_stats}")

command = f"python closest_node_by_type.py --type {snds_type}"
result, profile_stats = run_command_with_profiling(command)
_logger.info(f"Profiling Info: Command: {command}\nProfile Stats:\n{profile_stats}")
