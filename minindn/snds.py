from mininet.log                import setLogLevel, info
from minindn.minindn            import Minindn
from minindn.util               import MiniNDNCLI
from minindn.apps.app_manager   import AppManager
from minindn.apps.nfd           import Nfd
from minindn.apps.nlsr          import Nlsr
from time                       import sleep
from mininet.topo               import Topo

def run():
    Minindn.cleanUp()
    Minindn.verifyDependencies()

    ndn = Minindn()

    ndn.start()

    info('Starting NFD on nodes\n')
    nfds = AppManager(ndn, ndn.net.hosts, Nfd)
    info('Starting NLSR on nodes\n')
    nlsrs = AppManager(ndn, ndn.net.hosts, Nlsr)
    sleep(40)

    '''i = 0
    for host in ndn.net.hosts:
        host.cmd('export HOME=/tmp/minindn/' + host.name)
        host.cmd('python3 /home/minindn/snds/minindn/SDNS_r_service.py Type_' + host.name + ' &')
        host.cmd('python3 /home/minindn/snds/minindn/http_ngsild_proxy.py &')
        host.cmd('python3 /home/minindn/snds/minindn/ip_provider.py Type_' + host.name + ' item' + str(i))
        i = i + 1

    #for x in range(0, 1000):
    for k in range(0 , i):
        for host in ndn.net.hosts:
            host.cmd('export HOME=/tmp/minindn/' + host.name)
            host.cmd('(time python3 /home/minindn/snds/minindn/ip_consumerByID.py item' + str(k) + ') 2>> /tmp/minindn/' + host.name + '/' + host.name + '_id.txt')

    #for x in range(0, 1000):
    for host in ndn.net.hosts:
        for node in ndn.net.hosts:
            host.cmd('export HOME=/tmp/minindn/' + host.name)
            host.cmd('(time python3 /home/minindn/snds/minindn/ip_consumerByType.py Type_' + node.name + ') 2>> /tmp/minindn/' + host.name + '/' + host.name + '_type.txt') '''
               


    
    ############################ICSS experiment#############
    #run all services on all nodes
    for host in ndn.net.hosts:
        if host.name != 'forwarder':
             #print(host.name)
            host.cmd('export HOME=/tmp/minindn/' + host.name)
            host.cmd('python3 /home/minindn/snds/minindn/SNDS_r_service.py Type_' + host.name + ' &')
            host.cmd('python3 /home/minindn/snds/minindn/http_ngsild_proxy.py &')

    sleep(5)

    '''forwarder = ndn.net.hosts[0]
    forwarder.cmdPrint('tcpdump -i any -n -l -A -s0 > /tmp/minindn/packets.txt &')

    #===========================
    sleep(5)
    forwarder = ndn.net.hosts[0]
    forwarder.cmdPrint('tcpdump -i any -n -l -A -s0 > /tmp/minindn/cmd1.txt &')
    node4 = ndn.net.hosts[4]
    node4.cmd('export HOME=/tmp/minindn/node4')
    node4.cmdPrint('time python3 /home/minindn/snds/minindn/ip_provider.py Type_node4 item4 > /tmp/minindn/node4_pr.txt 2>&1')
    
    sleep(5)
    forwarder.cmdPrint('killall tcpdump; tcpdump -i any -n -l -A -s0 > /tmp/minindn/cmd2.txt &')
    node3 = ndn.net.hosts[3]
    node3.cmd('export HOME=/tmp/minindn/node3')
    node3.cmdPrint(' time python3 /home/minindn/snds/minindn/ip_provider.py Type_node2 item3 > /tmp/minindn/node3_pr.txt 2>&1')
    
    
	#===========================
	sleep(5)
    forwarder.cmdPrint('killall tcpdump; tcpdump -i any -n -l -A -s0 > /tmp/minindn/cmd3.txt &')
   
    node1 = ndn.net.hosts[1]
    node1.cmd('export HOME=/tmp/minindn/node1')
    node1.cmdPrint('time python3 /home/minindn/snds/minindn/ip_consumerByID.py Type_node4 item4 > /tmp/minindn/node1_con.txt 2>&1')

    sleep(5)
    forwarder.cmdPrint('killall tcpdump; tcpdump -i any -n -l -A -s0 > /tmp/minindn/cmd4.txt &')  
    node1.cmdPrint(' time python3 /home/minindn/snds/minindn/ip_consumerByType.py Type_node4  > /tmp/minindn/node1_con.txt 2>&1')
    
    
    #===========================
    sleep(5)
    forwarder.cmdPrint('killall tcpdump; tcpdump -i any -n -l -A -s0 > /tmp/minindn/cmd5.txt &')
   
    node4.cmd('export HOME=/tmp/minindn/node4')
    node4.cmdPrint('time python3 /home/minindn/snds/minindn/ip_consumerByID.py Type_node2 item3 > /tmp/minindn/node4_conID.txt 2>&1')
    sleep(2)
    forwarder.cmdPrint('killall tcpdump; tcpdump -i any -n -l -A -s0 > /tmp/minindn/cmd6txt &')
   
    node4.cmdPrint('time python3 /home/minindn/snds/minindn/ip_consumerByType.py Type_node2  > /tmp/minindn/node4_conType.txt 2>&1')
    #===========================
    
    
    sleep(5)
    
    forwarder.cmdPrint('killall tcpdump; tcpdump -i any -n -l -A -s0 > /tmp/minindn/cmd7.txt &')
   
    node4.cmdPrint('time python3 /home/minindn/snds/minindn/ip_consumerByID.py Type_node4 item4 >> /tmp/minindn/node4_con.txt 2>&1')

    sleep(5)
    forwarder.cmdPrint('killall tcpdump; tcpdump -i any -n -l -A -s0 > /tmp/minindn/cmd8.txt &')
   
    node4.cmdPrint('time python3 /home/minindn/snds/minindn/ip_consumerByType.py Type_node4  >> /tmp/minindn/node4_con.txt 2>&1')
	#===========================
    
    sleep(5)
    forwarder.cmdPrint('killall tcpdump; tcpdump -i any -n -l -A -s0 > /tmp/minindn/cmd9.txt &')
   
    node3.cmd('export HOME=/tmp/minindn/node3')
    node3.cmdPrint('time python3 /home/minindn/snds/minindn/ip_consumerByID.py Type_node2 item3 > /tmp/minindn/node3_con.txt') 
    
    sleep (5)
    forwarder.cmdPrint('killall tcpdump; tcpdump -i any -n -l -A -s0 > /tmp/minindn/cmd10.txt &')
   
    node3.cmdPrint('time python3 /home/minindn/snds/minindn/ip_consumerByType.py Type_node2  > /tmp/minindn/node3_con.txt') '''


    MiniNDNCLI(ndn.net)

    ndn.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
