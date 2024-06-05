import sys
import argparse
import logging
import os
from typing import Tuple, List

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

def keep_nodes_and_links(lines: List[str]) -> Tuple[List[str], List[str]]:
    """Extracts nodes and links from configuration lines.

    Args:
        lines (List[str]): Lines from the configuration file.

    Returns:
        Tuple[List[str], List[str]]: A tuple containing lists of links and nodes.
    """
    link_flag = False
    links: List[str] = []
    nodes: List[str] = []

    for line in lines: 
        line = line.strip()

        if line == "[links]":
            link_flag = True
            continue

        if line == "[nodes]":
            continue

        if link_flag:
            # Example line in file: MICHIGAN:NEU delay=14ms
            parts = line.split()
            links.append(parts[0])
            continue

        # Example line: UNIVH2C: _ radius=15.7232 angle=3.03408
        parts = line.split(":")
        nodes.append(parts[0])

    _logger.debug(f"Extracted links: {links}")
    _logger.debug(f"Extracted nodes: {nodes}")

    return links, nodes

def find_edge_nodes(nodes: List[str], links: List[str]) -> List[str]: 
    """Identifies edge nodes with two or fewer links.

    Args:
        nodes (List[str]): List of nodes.
        links (List[str]): List of links.

    Returns:
        List[str]: List of edge nodes.
    """
    edge_nodes: List[str] = []

    for node in nodes:
        link_count = sum(node in link for link in links)
        if link_count <= 2:
            edge_nodes.append(node)
    
    _logger.debug(f"Identified edge nodes: {edge_nodes}")
    return edge_nodes

def write_edge_nodes_to_disk(registry_filename: str, edge_nodes: List[str]):
    """Writes edge nodes to the registry file.

    Args:
        registry_filename (str): The registry filename.
        edge_nodes (List[str]): List of edge nodes to be written.
    """
    try:
        with open(registry_filename, "w") as f:
            for node in edge_nodes:
                f.write(f"{node.lower()}\n")
        _logger.info(f"Edge nodes written to {registry_filename}")
    except IOError as e:
        _logger.error(f"Error writing to {registry_filename}: {e}", file=sys.stderr)

def create_end_users(edge_nodes: List[str]) -> List[str]:
    """Creates end user nodes for each edge node.

    Args:
        edge_nodes (List[str]): List of edge nodes.

    Returns:
        List[str]: List of end user nodes.
    """
    end_users: List[str] = []
    for node in edge_nodes:
        for i in range(number_of_end_users):
            end_users.append(f"ue{node}{i}")

    _logger.debug(f"Created end users: {end_users}")
    return end_users

def create_new_topology_configuration_file(
    end_users: List[str],
    conf_file: str,
    lines_of_original_conf: List[str],
    edge_nodes: List[str]
):
    """Creates a new topology configuration file including end users.

    Args:
        end_users (List[str]): List of end user nodes.
        conf_file (str): Original configuration file name.
        lines_of_original_conf (List[str]): Lines of the original configuration file.
        edge_nodes (List[str]): List of edge nodes.
    """
    # Split the filename and extension
    file_name, file_extension = os.path.splitext(conf_file)
    new_conf_file = f"{file_name}_exp{file_extension}"

    try:
        with open(new_conf_file, "w") as f:
            f.write("[nodes]\n")
            for node in end_users:
                f.write(f"{node}:\n")

            # Write original nodes
            nodes_section = True
            for line in lines_of_original_conf:
                if line.strip() == "[nodes]":
                    continue
                if line.strip() == "[links]":
                    f.write("[links]\n")
                    nodes_section = False
                    continue
                f.write(line)

            #sanity check: if nodes section is finished write links
            if nodes_section:
                f.write("[links]\n")

            f.write("\n") 
            # Write new links
            for node in end_users:
                for edge_node in edge_nodes:
                    if edge_node in node: 
                        f.write(f"{node}:{edge_node} delay={delay_edge_users.strip()}\n")
                        
        _logger.info(f"New topology configuration file created: {new_conf_file}")
    except IOError as e:
        _logger.error(f"Error writing to {new_conf_file}: {e}", file=sys.stderr)

# Process each configuration file
for conf_file in conf_files:
    try:
        _logger.info(f"Processing configuration file: {conf_file}")
        with open(conf_file, 'r') as f:
            lines = f.readlines()
            links, nodes = keep_nodes_and_links(lines=lines)
            edge_nodes = find_edge_nodes(nodes=nodes, links=links)
            write_edge_nodes_to_disk(registry_filename=registry_filename, edge_nodes=edge_nodes)
            end_users = create_end_users(edge_nodes=edge_nodes)
            create_new_topology_configuration_file(end_users=end_users, conf_file=conf_file, lines_of_original_conf=lines, edge_nodes=edge_nodes)
    except IOError as e:
        _logger.error(f"Error reading {conf_file}: {e}", file=sys.stderr)
