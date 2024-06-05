import sys
import argparse
import logging
import os
from typing import Tuple, List
from utils import extract_nodes_and_links, write_edge_nodes_to_disk, identify_edge_nodes, create_end_users, create_new_topology_configuration_file

# Set up logging
_logger = logging.getLogger(os.path.basename(__file__))
_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
_logger.addHandler(stream_handler)

def parse_args():
    """Parses command-line arguments.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--end-users",
        type=int,
        required=True,
        help="Number of end users to be created per edge node."
    )

    parser.add_argument(
        "--registry-filename",
        type=str,
        default="./experiments/registry.txt",
        help="Filename for the registry where edge nodes are recorded."
    )

    parser.add_argument(
        "--delay-edge-users",
        type=str,
        default="10ms",
    )

    parser.add_argument(
        "--conf-files",
        nargs="+",
        required=True,
        help="List of configuration files to process."
    )

    return parser.parse_args()

args = parse_args()
number_of_end_users = args.end_users
conf_files = args.conf_files
registry_filename = args.registry_filename
delay_edge_users = args.delay_edge_users

_logger.info(f"Number of end users: {number_of_end_users}")
_logger.info(f"Registry filename: {registry_filename}")
_logger.info(f"Configuration files: {conf_files}")
_logger.info(f"Delay between edge nodes and users: {delay_edge_users}")


# Process each configuration file
for conf_file in conf_files:
    try:
        _logger.info(f"Processing configuration file: {conf_file}")
        with open(conf_file, 'r') as f:
            lines = f.readlines()
            links, nodes = extract_nodes_and_links(lines=lines)

            edge_nodes = identify_edge_nodes(
                nodes=nodes, 
                links=links
            )

            write_edge_nodes_to_disk(
                registry_filename=registry_filename, 
                edge_nodes=edge_nodes
            )

            end_users = create_end_users(
                edge_nodes=edge_nodes, 
                number_of_end_users=number_of_end_users
            )

            create_new_topology_configuration_file(
                end_users=end_users, 
                conf_file=conf_file, 
                lines_of_original_conf=lines, 
                edge_nodes=edge_nodes,
                delay_edge_users=delay_edge_users,
            )

    except IOError as e:
        _logger.error(f"Error reading {conf_file}: {e}", file=sys.stderr)
