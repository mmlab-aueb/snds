import os
import logging
import yaml
import argparse
import shlex


from mininet.log import MininetLogger
from minindn.minindn import Minindn
from minindn.util import MiniNDNCLI
from minindn.apps.app_manager import AppManager
from minindn.apps.nfd import Nfd
from minindn.apps.nlsr import Nlsr

#from dotenv import load_dotenv

from pprint import pprint
from time import sleep

# self made topology class
from prepare_workloads.utils import read_edge_nodes_from_registry
from Topology import CustomTopology

#load_dotenv()

background_service_pids = []

def setup_nodes(custom_topo: CustomTopology, yaml_path: str):

    _logger.info("Running setup on nodes\n")
    #read the script yaml file
    with open(yaml_path, 'r') as file:
        data = yaml.safe_load(file)

    for script in data['scripts']:
        for host_name in custom_topo.hosts_dictionary.keys():

            # Ensure the script is executable
            custom_topo.run_command_on_mininet_host(
                host_name=host_name,
                command=f"chmod u+x {script['path']}{script['name']}"
            )


            custom_topo.run_command_on_mininet_host(
                host_name=host_name,
                command=f"cp {script['path']}{script['name']} $HOME"
            )


            if not script['run_from_main']:
                continue

            env_vars_processed = []

            for i in range(0, len(script["environment_variables"]), 2):


                if i+1 < len(script["environment_variables"]):

                    # Provide the node_name as type
                    # If the type specified in the yaml is null
                    if script["environment_variables"][i+1] is None:  
                        condition = True if "type" in script['environment_variables'][i] else False

                        var = f"{script['environment_variables'][i]}=type_{host_name}" if condition else f"{script['environment_variables'][i]}={host_name}"

                        env_vars_processed.append(var)
                        continue

                    env_var = f"{script['environment_variables'][i]}={script['environment_variables'][i+1]}"

                env_vars_processed.append(shlex.quote(env_var))

            env_vars_processed.append(shlex.quote(f"--host-name={host_name}"))

            env_vars = " ".join(env_vars_processed)

            command = (
                f"mkdir -p $HOME/tmp/ && "
                f"mkdir -p $HOME/log/ && "
                f"mkdir -p $HOME/results/ &&"
                f"mkdir -p {script['log_path']}/{host_name}/ "
                f"mkdir -p {script['result_path']}/{host_name}/"
            )

            result = custom_topo.run_command_on_mininet_host(
                host_name=host_name,
                command=command
            )

            tcp_dump_command = f"tcpdump -i any -n -tttt | tee $HOME/results/{host_name}_packets.txt {script['result_path']}/{host_name}/{host_name}_packets.txt > /dev/null &"

            result = custom_topo.run_command_on_mininet_host(
                host_name=host_name,
                command=tcp_dump_command,
            )

            # Construct the command to log the nlsr and nfd logs
            #command = (
            #    f"inotifywait -m -r -e modify -e move -e create -e delete --format '%w%f' '/tmp/minindn/{host_name}/log' | "
            #    f"while read file; do "
            #    f"rsync -az '/tmp/minindn/{host_name}/log' '{script['log_path']}/{host_name}/' ; "
            #    f"done &"
            #)

            result = custom_topo.run_command_on_mininet_host(
                host_name=host_name,
                command=command
            )

            if len(result.split()) == 2:
                _, pid = result.split()
                background_service_pids.append({"host_name": host_name, "pid": pid})

            # Construct the command
            command = (
                f"python {script['path']}{script['name']} {env_vars} "
                f"2>&1 | tee {script['log_path']}/{host_name}/{script['log']}"
            )

            if script["background_service"]:
                command += ' &'

            result = custom_topo.run_command_on_mininet_host(
                host_name=host_name,
                command=command
            )

            if len(result.split()) == 2:
                _, pid = result.split()
                background_service_pids.append({"host_name": host_name, "pid": pid})


def run():
    try:

        Minindn.cleanUp()
        Minindn.verifyDependencies()

        # Parse all arguments
        args = Minindn.parseArgs(argparse.ArgumentParser()).parse_args()

        custom_topo = CustomTopology()

        faces = None
        _, faces = custom_topo.processTopo(args.topoFile)

        _logger.debug(f"Nodes inside custom topo: {pprint(custom_topo.g.node)}\n")
        _logger.debug(f"Edges inside custom topo: {pprint(custom_topo.g.edge)}")


        ndn = Minindn(topo=custom_topo)

        ndn.setupFaces(faces)

        ndn.start()

        for host in ndn.net.hosts:
            _logger.debug(f"Node: {host.params}\n")

        _logger.info('Starting NFD on nodes\n')
        nfds = AppManager(ndn, ndn.net.hosts, Nfd, logLevel="DEBUG")
        _logger.info('Starting NLSR on nodes\n')
        nlsrs = AppManager(ndn, ndn.net.hosts, Nlsr)

        sleep(40)

        hosts = [host for host in ndn.net.hosts if "ue" not in host.name]
        _logger.debug(f"Non edge hosts:\n{hosts}\n")

        edge_hosts = [host for host in ndn.net.hosts if "ue" in host.name]
        _logger.debug(f"Edge hosts:\n{edge_hosts}\n")

        edge_nodes = read_edge_nodes_from_registry(
            registry_filename="./prepare_workloads/experiments/registry.txt",
        )

        _logger.debug(f"Edge nodes:\n{edge_nodes}\n")

        number_of_end_users = len(edge_nodes)

        _logger.debug(f"Number of end users: {number_of_end_users}\n")

        custom_topo.add_mininet_hosts(hosts=hosts)
        custom_topo.add_mininet_hosts(hosts=edge_hosts)
        _logger.debug(f"Mininet hosts:\n{custom_topo.mininet_hosts}\n")

        setup_nodes(custom_topo, './scripts_for_nodes_config.yaml')

        MiniNDNCLI(ndn.net)

        ndn.stop()
    except Exception as e:
        # Log the error message
        _logger.error(f"An error occurred: {e}\n")

        # Log the type of the exception
        _logger.error(f"Exception type: {type(e).__name__}\n")

        # Get a full traceback
        import traceback
        tb = traceback.format_exc()
        _logger.error(f"Traceback: {tb}\n")

    except BaseException as e:
        # This will catch everything, including KeyboardInterrupt, SystemExit, etc.
        _logger.error(f"A non-standard exception occurred: {e}\n")

        # Log the type of the exception
        _logger.error(f"Exception type: {type(e).__name__}\n")

        # Get a full traceback
        import traceback
        tb = traceback.format_exc()
        _logger.error(f"Traceback: {tb}\n")

    finally:
        # Assume background_service_pids holds PIDs of the background services
        for service in background_service_pids:

            pid = service["pid"]
            host_name = service["host_name"]

            kill_command = f"kill {pid}"

            # Execute the kill command on the appropriate host
            # Assuming `host_name` is known or determined earlier
            kill_result = custom_topo.run_command_on_mininet_host(
                host_name=host_name,
                command=kill_command,
            )

        Minindn.handleException()

if __name__ == '__main__':
    # Define a new logging format
    standard_logging = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    _logger = MininetLogger(os.path.basename(__file__))
    #TODO hardcoded log level
    _logger.setLogLevel('debug')

    for handler in _logger.handlers:
        handler.setFormatter(logging.Formatter(standard_logging))

    run()


