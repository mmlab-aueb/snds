import sys
import random

number_of_endUsers = sys.argv[1]

edge_nodes = []
with open("registry.txt", "r") as file:
    for line in file:
        edge_nodes.append(line.strip())

#print(edge_nodes)

with open("workload_provide_" + number_of_endUsers + ".txt", "w") as file:
    for node in edge_nodes:
        for i in range(0, int(number_of_endUsers)):
            file.write(str(i) + " ue" + node + "" + str(i) + " provide Type_" + node + " item" + node + "" + str(i) + '\n')

with open("workload_consume_" + number_of_endUsers + ".txt", "w") as file:
    for node in edge_nodes:
        for i in range(0, int(number_of_endUsers)):
            for node1 in edge_nodes:
                for i1 in range(0, int(number_of_endUsers)):
                    if node != node1:
                        file.write(str(i) + " ue" + node + "" + str(i) + " consumeID Type_" + node1 + " item" + node1 + "" + str(i1) + '\n')
                    elif i != i1:
                        file.write(str(i) + " ue" + node + "" + str(i) + " consumeID Type_" + node1 + " item" + node1 + "" + str(i1) + '\n')

lines = open("workload_consume_" + number_of_endUsers + ".txt").readlines()
random.shuffle(lines)
open("workload_consume_" + number_of_endUsers + ".txt", "w").writelines(lines)

with open("workload_" + number_of_endUsers + ".txt", "w") as file:
    lines = open("workload_provide_" + number_of_endUsers + ".txt").read()
    lines1 = open("workload_consume_" + number_of_endUsers + ".txt").read()

    file.write(lines)
    file.write(lines1)