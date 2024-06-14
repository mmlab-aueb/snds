import os
import argparse

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

os.popen(f"python closest_node_by_id.py --id {snds_id}")
os.popen(f"python closest_node_by_type.py --type {snds_type}")