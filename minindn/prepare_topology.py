import sys

number_of_endUsers = sys.argv[1]

#read the testbed topology configuration file
with open('testbed.conf', 'r') as f:
    lines = f.readlines()

#print(lines)

#keep the nodes and the links
links = []
nodes = []
flag = False
for line in lines:
    line = line.strip()

    if line == '[links]':
        #print(line)
        flag = True
        continue

    if line == '[nodes]':
        continue
    
    if flag == False:
        #print(line)
        parts = line.split(':')
        #print(parts[0])
        nodes.append(parts[0])

    if flag:
        #print(line)
        parts = line.split()
        #print(parts)
        links.append(parts[0])

#print(links)
#print(nodes)

#find the edge nodes (nodes having <=2 links)
edge_nodes =[]
counter = 0
for node in nodes:
    for link in links:
        if node in link:
            counter = counter + 1
    if counter <= 2:
        edge_nodes.append(node)
    counter = 0

#write the edge nodes to a file
with open("registry.txt", "w") as file:
    for node in edge_nodes:
        file.write(node.lower() + '\n')

#print(edge_nodes)
#print(len(edge_nodes))

#create the end users depending on the argument number of end users
endUsers = []
for node in edge_nodes: 
    print(node)
    for i in range(int(number_of_endUsers)):
        endUsers.append('ue' + node + '' + str(i))

#print(endUsers)

#create the new topology configuration file which will have the newly added end users with the corresponding links
with open("testbed_exp.conf", "w") as file:
    file.write('[nodes]\n')
    for node in endUsers:
        file.write(node + ':\n')
    for line in lines:
        if line == '[nodes]\n':
            continue
        file.write(line)
    file.write('\n')
    for node in endUsers:
        for edgeNode in edge_nodes:
            if edgeNode in node:
                file.write(node + ':' + edgeNode + ' delay=10ms\n')
