# SNDS mininet
This folder includes mininet scripts that setup a simple topology, which can be used for validating NDN application for the SNDS project.

## Prerequisites 
* Install NFD from [sources](https://github.com/named-data/NFD)
* Install mininet with python3 support (`sudo PYTHON=python3 mininet/util/install.sh -n`) 
* Install [infoedit](https://github.com/NDN-Routing/infoedit) 
* Install `python-ndn` as global module (`sudo -H pip3 install python-ndn`)

## Execution
Run `sudo killall nfd & sleep 0.5 && sudo mn -c && sudo python3 snds_topology.py`. Then, in the `mininet>` command prompt run `xterm consumer producer closest`. In the xterm of `producer` run: 
```
export HOME=/tmp/mininet/producer
python3 snds_producer.py
```
In the xterm of `consumer` run:
```
export HOME=/tmp/mininet/consumer
python3 snds_consumer.py
```
In the xterm of `closest` run:
```
export HOME=/tmp/mininet/closest
python3 closestCDNNode_byID.py
```
or
`python3 closestCDNNode_byType.py` for the second scenario.