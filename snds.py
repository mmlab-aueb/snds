import os 
import logging
import yaml
import shlex

from time import sleep

from mininet.log import MininetLogger
from minindn.minindn import Minindn
from minindn.util import MiniNDNCLI
from minindn.apps.app_manager import AppManager
from minindn.apps.nfd import Nfd 
from minindn.apps.nlsr import Nlsr

#from dotenv import load_dotenv

# self made topology class
from Topology import CustomTopology

#load_dotenv()

background_service_pids = []

def setup_nodes(topo: CustomTopology, yaml_path: str):


    #read the script yaml file 
    with open(yaml_path, 'r') as file: 
        data = yaml.safe_load(file)

    for script in data['scripts']:
        for host_name in topo.hosts_dictionary.keys():

            # Ensure the script is executable
            topo.run_command_on_mininet_host(
                host_name=host_name,
                command=f"chmod u+x {script['path']}{script['name']}"
            )


            if not script['run_from_main']:
                continue

            env_vars_processed = []

            for i in range(0, len(script["environment_variables"]), 2):

                if i+1 < len(script["environment_variables"]): 
                    env_var = f"{script['environment_variables'][i]}={script['environment_variables'][i+1]}"

                env_vars_processed.append(shlex.quote(env_var))
           
            env_vars_processed.append(shlex.quote(f"--host-name={host_name}"))

            env_vars = " ".join(env_vars_processed)

            command = (
                f"mkdir -p $HOME/tmp/ && "
                f"mkdir -p $HOME/log/ && "
                f"mkdir -p {script['log_path']}/{host_name}/ "
            )


            result = topo.run_command_on_mininet_host(
                host_name=host_name,
                command=command
            )

            # Construct the command
            command = (
                f"inotifywait -m -r -e modify -e move -e create -e delete --format '%w%f' '/tmp/minindn/{host_name}/log' | "
                f"while read file; do "
                f"rsync -az '/tmp/minindn/{host_name}/log' '{script['log_path']}/{host_name}/' ; "
                f"done &"
            )

            result = topo.run_command_on_mininet_host(
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

            result = topo.run_command_on_mininet_host(
                host_name=host_name,
                command=command
            )

            if len(result.split()) == 2: 
                _, pid = result.split()
                background_service_pids.append({"host_name": host_name, "pid": pid})

    
def run(_logger: MininetLogger):
    try: 

        Minindn.cleanUp()
        Minindn.verifyDependencies()
        topo = CustomTopology()

        #Define hosts
        #TODO hardcoded hosts 
        hosts = {
            'producer': '10.0.0.1/8',
            'forwarder': '10.0.0.2/8',
            'consumer': '10.0.0.3/8',
            'closest': '10.0.0.4/8',
            'ngsild': '10.0.0.5/8'
        }

        _logger.info("Read hosts from environment variables\n")

        topo.add_hosts(hosts)
        topo.add_switch('switch1')

        for host_name, _ in topo.hosts_dictionary.items(): 
            topo.add_switch_link_for_host(host_name, 'switch1', delay='10ms')


        ndn = Minindn(topo=topo)

        ndn.start()

        for host in ndn.net.hosts: 
            _logger.debug(f"Node: {host.params}\n")
        _logger.info('Starting NFD on nodes\n')
        nfds = AppManager(ndn, ndn.net.hosts, Nfd, logLevel="DEBUG")
        _logger.info('Starting NLSR on nodes\n')
        nlsrs = AppManager(ndn, ndn.net.hosts, Nlsr)

        topo.add_mininet_hosts(ndn.net.hosts)

        setup_nodes(topo, './scripts_for_nodes_config.yaml')

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
            kill_result = topo.run_command_on_mininet_host(
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

    run(_logger)

        

