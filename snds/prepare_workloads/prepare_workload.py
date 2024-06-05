import sys
import random
import argparse

from utils import read_edge_nodes_from_registry, create_consume_workload, create_provide_workload, create_combined_workload

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
    )

    parser.add_argument(
        "--registry-filename",
        type=str,
        default="./experiments/registry.txt",
        help="Filename for the registry where edge nodes are recorded."
    )


    return parser.parse_args()

args = parse_args()
registry_filename = args.registry_filename
number_of_end_users = args.end_users

edge_nodes = read_edge_nodes_from_registry(registry_filename=registry_filename)

workload_provide_filename = f"./experiments/workload_provide_{number_of_end_users}.txt"
workload_consume_filename = f"./experiments/workload_consume_{number_of_end_users}.txt"

create_provide_workload(
    workload_filename=workload_provide_filename,
    edge_nodes=edge_nodes,
    number_of_end_users=number_of_end_users,
)

create_consume_workload(
    workload_filename=workload_consume_filename,
    edge_nodes=edge_nodes,
    number_of_end_users=number_of_end_users,
)

create_combined_workload(
    workload_consume_filename=workload_consume_filename,
    workload_provide_filename=workload_provide_filename,
    number_of_end_users=number_of_end_users,
)
