import os 
import logging

from mininet.log import MininetLogger
from minindn.minindn import Minindn
from minindn.util import MiniNDNCLI
from minindn.apps.app_manager import AppManager
from minindn.apps.nfd import Nfd
from minindn.apps.nlsr import Nlsr

from time import sleep
#from dotenv import load_dotenv

# self made topology class
from Topology import CustomTopology

#load_dotenv()

# Define a new logging format
standard_logging = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


def run():
    try: 

        Minindn.cleanUp()
        Minindn.verifyDependencies()
        topo = CustomTopology()

        #Define hosts
        hosts = {
            'producer'  : os.getenv('PRODUCER_HOSTNAME'),
            'forwarder' : os.getenv('FORWARDER_HOSTNAME'),
            'consumer'  : os.getenv('CONSUMER_HOSTNAME'),
            'closest'   : os.getenv('CLOSEST_HOSTNAME'),
            'ngsild'    : os.getenv('NGSILD_HOSTNAME')       
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
        sleep(90)


        for host in ndn.net.hosts: 
            _logger.debug(f"Parsing host {host} to run service.\n")


        MiniNDNCLI(ndn.net)

        ndn.stop()
    except Exception as e: 
        Minindn.handleException()
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    _logger = MininetLogger(os.path.basename(__file__))
    _logger.setLogLevel(os.getenv('LOG_LEVEL', 'info'))
    for handler in _logger.handlers:
        handler.setFormatter(logging.Formatter(standard_logging))
    run()
        

