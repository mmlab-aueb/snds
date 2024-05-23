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
    sleep(90)


    #run all services on all nodes except to end users
    for host in ndn.net.hosts:
        if "ue" not in host.name:
            host.cmd('export HOME=/tmp/minindn/' + host.name)
            #host.cmd('python3 /home/minindn/snds/minindn/SNDS_r_service.py Type_' + host.name + ' &')
            #host.cmd('python3 /home/minindn/snds/minindn/http_ngsild_proxy.py &')
            host.cmd('tcpdump -i any -n -tttt > /tmp/minindn/results/' + host.name + '_packets.txt &')

    

    #read the edge nodes from the registry txt
    edge_nodes = []
    with open("experiments/registry.txt", "r") as file:
        for line in file:
            edge_nodes.append(line.strip())

    #print(edge_nodes)

    for node in edge_nodes:
        edge_node = ndn.net[node]
        edge_node.cmd('export HOME=/tmp/minindn/' + edge_node.name)
        edge_node.cmd('python3 /home/minindn/snds/minindn/SNDS_r_service.py Type_' + edge_node.name + ' &')
        edge_node.cmd('python3 /home/minindn/snds/minindn/http_ngsild_proxy.py  >> /tmp/minindn/' + edge_node.name + '/proxy.txt &')

    sleep(300)


    number_of_endUsers = 5

    #create a map, edgeNodes ---> IPs
    edge_nodes_ips = {}
    for node in edge_nodes:
        edge_node = ndn.net[node]
        interfaces = edge_node.intfNames()
        ips = []
        for name in interfaces:
            #print(edge_node)
            #print(name)
            #print(edge_node.IP(intf=name))
            ips.append(edge_node.IP(intf=name))
        edge_nodes_ips[edge_node.name] = ips

    #print(len(edge_nodes_ips["gist"]))

    #read the workload
    rows = []
    with open("experiments/workload_5.txt", "r") as file:
        for line in file:
            rows.append(line.split())

    #print(rows)

    for row in rows:
        print("TEST!")
        #print(row[0])
        #sleep(int(row[0]))
        sleep(1)
        user = ndn.net[row[1].lower()]
        number_of_user = ''.join(filter(str.isdigit, user.name))
        #print(user.name + ' ' + number_of_user)
        for node in edge_nodes:
            if node.casefold() in user.name.casefold():
                edge_node = node
            #print(edge_node)
        ip = number_of_endUsers - int(number_of_user)
        edge_node_ip = edge_nodes_ips[edge_node][len(edge_nodes_ips[edge_node])-ip]
        #print(edge_node_ip)
        if row[2] == "provide":
            #print("provide")
            user.cmdPrint('time python3 /home/minindn/snds/minindn/ip_provider.py ' + row[3] + ' ' + row[4]  + ' ' + edge_node_ip + ' >> /tmp/minindn/provide.txt 2>&1')
        elif row[2] == "consumeID":
            print("consumeID")
            user.cmdPrint('time python3 /home/minindn/snds/minindn/ip_consumerByID.py ' + row[3] + ' ' + row[4]  + ' ' + edge_node_ip + ' >> /tmp/minindn/consumeID.txt 2>&1')
        elif row[2] == "consumeType":
            #print("consumeType")
            user.cmdPrint('time python3 /home/minindn/snds/minindn/ip_consumerByType.py ' + row[3] + ' ' + edge_node_ip + ' >> /tmp/minindn/consumeType.txt 2>&1')

    for host in ndn.net.hosts:
        if "ue" not in host.name:
            host.cmd('export HOME=/tmp/minindn/' + host.name)
            host.cmd('pkill tcpdump')


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
