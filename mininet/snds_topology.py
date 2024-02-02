#!/usr/bin/python

from mininet.net    import  Mininet
from mininet.topo   import  Topo
from mininet.cli    import  CLI
from mininet.log    import  lg, info

import time
import subprocess

class NDNTopo(Topo):

    '''
                    closest CDN node(10.0.0.4)
                                |
                                |
                                |
                        forwarder(10.0.0.2)
                                |
                                |
                                |
    producer(10.0.0.1)<---->(switch)<---->consumer(10.0.0.3)
    '''

    def build(self):

        #Define hosts
        hosts = {
            'producer'  : '10.0.0.1/8',
            'forwarder' : '10.0.0.2/8',
            'consumer'  : '10.0.0.3/8',
            'closest'   : '10.0.0.4/8',
            'ngsild'    : '10.0.0.5/8'       
        }

        #Add switch
        s1 = self.addSwitch('s1')

        #Add hosts and links
        for host,ip in hosts.items():
            h = self.addHost(host, ip=ip)
            print("Added host ", host, "with ip ", ip)
            self.addLink(s1, h)

    def configure_faces(self, net):

        '''
                                closest CDN node (10.0.0.4)
                                            |
                                            |
            producer(10.0.0.1)<---->forwarder(10.0.0.2)<---->consumer(10.0.0.3)
                    |                                               |
                    |                                               |
            snds/CAR, snds/CAR_registry                    snds/Car1, snds/rID
        '''

        #producer
        producer = net.hosts[0]
        producer.cmd('export HOME=/tmp/mininet/producer')
        producer.cmd('nfdc face create udp://10.0.0.2')
        producer.cmd('nfdc route add /snds/Car1 udp://10.0.0.2')

        #forwarder
        forwarder = net.hosts[1]
        forwarder.cmd('export HOME=/tmp/mininet/forwarder')
        forwarder.cmd('nfdc face create udp://10.0.0.1')
        forwarder.cmd('nfdc face create udp://10.0.0.3')
        forwarder.cmd('nfdc route add /snds/CAR udp://10.0.0.1')
        forwarder.cmd('nfdc route add /snds/CAR_registry udp://10.0.0.1')
        forwarder.cmd('nfdc route add /snds/Car1 udp://10.0.0.3')

        #consumer
        consumer = net.hosts[2]
        consumer.cmd('export HOME=/tmp/mininet/consumer')
        consumer.cmd('nfdc face create udp://10.0.0.2')
        consumer.cmd('nfdc route add /snds/CAR udp://10.0.0.2')
        consumer.cmd('nfdc route add /snds/CAR_registry udp://10.0.0.2')

        #closest CDN node
        closest = net.hosts[3]
        closest.cmd('export HOME=/tmp/mininet/closest')
        closest.cmd('nfdc face create udp://10.0.0.2')

        #test
        ngsild = net.hosts[4]
        ngsild.cmd('export HOME=/tmp/mininet/ngsild')
        ngsild.cmd('nfdc face create udp://10.0.0.2')

        print("Faces configured!")

def start_nfd(net):
    for node in net.hosts:
        homeDir = '/tmp/mininet/{}'.format(node.name)
        node.cmd('rm -rf {}'.format(homeDir)) # fresh start
        node.cmd('mkdir -p {}'.format(homeDir))
        node.cmd('export HOME={} && cd ~'.format(homeDir))
        ndnFolder  = '{}/.ndn'.format(homeDir)
        node.cmd('mkdir -p {}'.format(ndnFolder))
        confFile   = '{}/nfd.conf'.format(homeDir)
        logFile    = 'nfd.log'
        sockFile   = '/run/{}.sock'.format(node.name)
        clientConf = '{}/client.conf'.format(ndnFolder)
        node.cmd('cp /usr/local/etc/ndn/nfd.conf.sample {}'.format(confFile))
        node.cmd('cp /usr/local/etc/ndn/client.conf.sample {}'.format(clientConf))
        #Open the conf file and change socket file name
        node.cmd('infoedit -f {} -s face_system.unix.path -v {}'.format(confFile, sockFile))
    
        #Change the unix socket
        node.cmd('sudo sed -i "s|;transport|transport|g" {}'.format(clientConf))
        node.cmd('sudo sed -i "s|nfd.sock|{}.sock|g" {}'.format(node.name, clientConf))
        #Create the certificate
        node.cmd('ndnsec-key-gen /snds | ndnsec-cert-install -')
        print("nfd is starting in {}  with config file {}".format(node.name, confFile))
        node.cmd('nfd --config {} > {}/nfd.out  2>&1&'.format(confFile, homeDir))

def runNDNTopo():
    topo = NDNTopo()
    net = Mininet(topo=topo)
    net.start()
    time.sleep(2)

    start_nfd(net)
    time.sleep(2)
    
    topo.configure_faces(net)

    '''
    # run scripts
    producer = net.hosts[0]
    producer.cmd('export HOME=/tmp/mininet/producer')
    producer.cmd('python3 /home/snds/Desktop/mininet/snds_producer.py > /tmp/Producer 2>&1&')

    time.sleep(5)

    consumer = net.hosts[2]
    consumer.cmd('export HOME=/tmp/mininet/consumer')
    consumer.cmd('python3 /home/snds/Desktop/mininet/snds_consumer.py > /tmp/Consumer 2>&1&')

    time.sleep(5)

    closest = net.hosts[3]
    closest.cmd('export HOME=/tmp/mininet/closest')
    closest.cmd('python3 /home/snds/Desktop/mininet/closestCDNNode_byID.py > /tmp/closest')
    time.sleep(5)
    closest.cmd('python3 /home/snds/Desktop/mininet/closestCDNNode_byType.py >> /tmp/closest')
    '''

    print
    info("*** Hosts are running and should have internet connectivity\n")
    info("*** Type 'exit' or control-D to shut down network\n")

    CLI(net)

    #Shutdown
    subprocess.run(["nfd-stop"])
    net.stop()

if __name__ == '__main__':
    lg.setLogLevel('info')
    runNDNTopo()
        