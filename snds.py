import os 
import logging
import yaml

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

            # Join environment variables with spaces
            env_vars = " ".join(script['environment_variables'])

            # Construct the command, ensuring proper path and log file handling
            command = (
                f"mkdir -p $HOME/tmp/ && "
                f"mkdir -p {script['log_path']} && "
                f"python {script['path']}{script['name']} {env_vars} "
                f"2>&1 | tee $HOME/tmp/{script['log']} {script['log_path']}{script['log']} &"
            )

            topo.run_command_on_mininet_host(
                host_name=host_name,
                command=command
            )

    
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

        _logger.info('Starting NFD on nodes\n')
        nfds = AppManager(ndn, ndn.net.hosts, Nfd)
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

        #sanity check shutdown http server
        topo.run_command_on_mininet_host(
            host_name='ngsild', 
            command=f'kill -SIGTERM {http_pid}'
        )

        #sanity check shutdown producer server
        topo.run_command_on_mininet_host(
            host_name='ngsild', 
            command=f'kill -SIGTERM {producer_pid}'
        )
        Minindn.handleException()

if __name__ == '__main__':
    global http_pid, producer_pid
    http_pid = -1
    producer_pid = -1
    # Define a new logging format
    standard_logging = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    _logger = MininetLogger(os.path.basename(__file__))
    #TODO hardcoded log level
    _logger.setLogLevel('debug')

    for handler in _logger.handlers:
        handler.setFormatter(logging.Formatter(standard_logging))

    run(_logger)

        

