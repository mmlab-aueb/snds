import logging
import sys
import os
import itertools
import random
from typing import Tuple, List

_logger = logging.getLogger(os.path.basename(__file__))
_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
_logger.addHandler(stream_handler)

def extract_nodes_and_links(lines: List[str]) -> Tuple[List[str], List[str]]:
    """Extracts nodes and links from configuration lines.

    Args:
        lines (List[str]): Lines from the configuration file.

    Returns:
        Tuple[List[str], List[str]]: A tuple containing lists of links and nodes.

    Example:
        lines = [
            "[nodes]",
            "UNIVH2C: _ radius=15.7232 angle=3.03408",
            "[links]",
            "MICHIGAN:NEU delay=14ms"
        ]
        links, nodes = extract_nodes_and_links(lines)
        print(links)  # Output: ['MICHIGAN:NEU']
        print(nodes)  # Output: ['UNIVH2C']
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

def read_edge_nodes_from_registry(registry_filename: str) -> List[str]:
    """Reads edge nodes from a registry file.

    Args:
        registry_filename (str): The registry filename.

    Returns:
        List[str]: List of edge nodes.

    Example:
        edge_nodes = read_edge_nodes_from_registry("registry.txt")
        print(edge_nodes)  # Output: ['UNIVH2C', 'MINHO', ...]
    """
    edge_nodes: List[str] = []

    with open(registry_filename, "r") as f:
        for line in f:
            edge_nodes.append(line.strip())

    _logger.debug(f"Read edge nodes: {edge_nodes}")    

    return edge_nodes

def create_provide_workload(
    workload_filename: str, 
    edge_nodes: List[str],
    number_of_end_users: int,
):
    """Creates a provide workload file for edge nodes.

    Args:
        workload_filename (str): The filename to write the provide workload.
        edge_nodes (List[str]): List of edge nodes.
        number_of_end_users (int): Number of end users.

    Example:
        create_provide_workload("workload_provide.txt", ["UNIVH2C", "MINHO"], 5)
    """
    with open(workload_filename, "w") as f:
        for node in edge_nodes:
            for i in range(number_of_end_users):
                f.write(f"{i} ue{node}ID{i} provide type_{node} item{node}ID{i}\n")

def create_consume_workload(
    workload_filename: str, 
    edge_nodes: List[str],
    number_of_end_users: int,
):
    """Creates a consume workload file for edge nodes.

    Args:
        workload_filename (str): The filename to write the consume workload.
        edge_nodes (List[str]): List of edge nodes.
        number_of_end_users (int): Number of end users.

    Example:
        create_consume_workload("workload_consume.txt", ["UNIVH2C", "MINHO"], 5)
    """
    with open(workload_filename, "w") as file:
        # All combinations using Cartesian product
        for node, i, other_node, j in itertools.product(
            edge_nodes, 
            range(number_of_end_users), 
            edge_nodes, 
            range(number_of_end_users),
        ):
            if node != other_node or i != j:
                ue_node = f"ue{node}ID{i}"
                item_node = f"item{other_node}ID{j}"
                file.write(f"{i} {ue_node} consumeID type_{other_node} {item_node}\n")

def create_combined_workload(
    workload_consume_filename: str,
    workload_provide_filename: str,
    number_of_end_users: int,
):
    """Combines provide and consume workloads into a single file.

    Args:
        workload_consume_filename (str): The consume workload filename.
        workload_provide_filename (str): The provide workload filename.
        number_of_end_users (int): Number of end users.

    Example:
        create_combined_workload("workload_consume.txt", "workload_provide.txt", 5)
    """
    workload_combined_filename = f"./experiments/workload_{number_of_end_users}.txt"

    # Read and shuffle the consume workload
    with open(workload_consume_filename, "r") as consume_file:
        consume_lines = consume_file.readlines()

    random.shuffle(consume_lines)

    with open(workload_consume_filename, "w") as consume_file:
        consume_file.writelines(consume_lines)

    # Combine provide and shuffled consume workloads into the output file
    with open(workload_combined_filename, "w") as outfile, \
         open(workload_provide_filename, "r") as provide_file, \
         open(workload_consume_filename, "r") as consume_file:

        # Write provide workload to the output file
        outfile.write(provide_file.read())

        # Write shuffled consume workload to the output file
        outfile.write(consume_file.read())

def read_workload(file_path: str) -> List[List[str]]:
    """
    Reads the workload file and returns a list of rows.

    Args:
        file_path (str): The path to the workload file.

    Returns:
        List[List[str]]: A list of rows, where each row is a list of strings.

    Example:
        >>> read_workload("experiments/workload_5.txt")
        [['1', 'UserA', 'provide', 'param1', 'param2'],
         ['2', 'UserB', 'consumeID', 'param3', 'param4']]
    """
    with open(file_path, "r") as file:
        return [line.strip().split() for line in file]

def identify_edge_nodes(nodes: List[str], links: List[str]) -> List[str]: 
    """Identifies edge nodes with two or fewer links.

    Args:
        nodes (List[str]): List of nodes.
        links (List[str]): List of links.

    Returns:
        List[str]: List of edge nodes.

    Example:
        nodes = ["UNIVH2C", "MINHO", "MSU"]
        links = ["UNIVH2C:MINHO", "MSU:MINHO"]
        edge_nodes = identify_edge_nodes(nodes, links)
        print(edge_nodes)  # Output: ["UNIVH2C", "MSU"]
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

    Example:
        write_edge_nodes_to_disk("registry.txt", ["UNIVH2C", "MINHO"])
    """
    try:
        with open(registry_filename, "w") as f:
            for node in edge_nodes:
                f.write(f"{node.lower()}\n")
        _logger.info(f"Edge nodes written to {registry_filename}")
    except IOError as e:
        _logger.error(f"Error writing to {registry_filename}: {e}", file=sys.stderr)

def create_end_users(
    edge_nodes: List[str], 
    number_of_end_users: int,
) -> List[str]:
    """Creates end user nodes for each edge node.

    Args:
        edge_nodes (List[str]): List of edge nodes.
        number_of_end_users (int): Number of end users.

    Returns:
        List[str]: List of end user nodes.

    Example:
        edge_nodes = ["UNIVH2C", "MINHO"]
        end_users = create_end_users(edge_nodes, 5)
        print(end_users)  # Output: ["ueUNIVH2C0", "ueUNIVH2C1", ..., "ueMINHO4"]
    """
    end_users: List[str] = []
    for node in edge_nodes:
        for i in range(number_of_end_users):
            end_users.append(f"ue{node}ID{i}")

    _logger.debug(f"Created end users: {end_users}")
    return end_users

def create_new_topology_configuration_file(
    end_users: List[str],
    conf_file: str,
    lines_of_original_conf: List[str],
    edge_nodes: List[str],
    delay_edge_users: str,
):
    """Creates a new topology configuration file including end users.

    Args:
        end_users (List[str]): List of end user nodes.
        conf_file (str): Original configuration file name.
        lines_of_original_conf (List[str]): Lines of the original configuration file.
        edge_nodes (List[str]): List of edge nodes.
        delay_edge_users (str): Amount of delay between the users and the edge nodes.

    Example:
        end_users = ["ueUNIVH2C0", "ueUNIVH2C1"]
        edge_nodes = ["UNIVH2C", "MINHO"]
        lines_of_original_conf = ["[nodes]", "UNIVH2C: _ radius=15.7232 angle=3.03408", "[links]", "MICHIGAN:NEU delay=14ms"]
        create_new_topology_configuration_file(end_users, "config.txt", lines_of_original_conf, edge_nodes, "14ms")
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

            # Sanity check: if nodes section is finished write links
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
