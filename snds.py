import os 

from mininet.log import setLogLevel, info
from minindn.minindn import Minindn
from minindn.util import MiniNDNCLI
from minindn.apps.app_manager import AppManager
from minindn.apps.nfd import Nfd
from minindn.apps.nlsr import Nlsr

from time import sleep
from dotenv import load_dotenv

# self made topology class
from Topology import CustomTopology

load_dotenv()


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

        info("Read hosts from environment variables\n")

        topo.add_hosts(hosts)
        topo.add_switch('switch1')

        print(topo.hosts_dictionary)
        print(topo.switches_dictionary)

       
        for host_name, _ in topo.hosts_dictionary.items(): 
            topo.add_switch_link_for_host(host_name, 'switch1', delay='10ms')

        #print(topo.hosts()) 
        #print(topo.links())
        #print(topo.switches())

        ndn = Minindn(topo=topo)

        ndn.start()

        info('Starting NFD on nodes\n')
        nfds = AppManager(ndn, ndn.net.hosts, Nfd)
        info('Starting NLSR on nodes\n')
        nlsrs = AppManager(ndn, ndn.net.hosts, Nlsr)
        sleep(90)

        MiniNDNCLI(ndn.net)

        ndn.stop()
    except Exception as e: 
        Minindn.handleException()
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    setLogLevel(os.getenv('LOG_LEVEL'))
    run()
        

